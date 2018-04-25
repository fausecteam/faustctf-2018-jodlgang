import numpy as np


def get_im2col_indices_org(x_shape, field_height, field_width, padding=1, stride=1):
  # First figure out what the size of the output should be
  N, C, H, W = x_shape
  assert (H + 2 * padding - field_height) % stride == 0
  assert (W + 2 * padding - field_height) % stride == 0
  out_height = (H + 2 * padding - field_height) // stride + 1
  out_width = (W + 2 * padding - field_width) // stride + 1

  i0 = np.repeat(np.arange(field_height), field_width)
  i0 = np.tile(i0, C)
  i1 = stride * np.repeat(np.arange(out_height), out_width)
  j0 = np.tile(np.arange(field_width), field_height * C)
  j1 = stride * np.tile(np.arange(out_width), out_height)
  i = i0.reshape(-1, 1) + i1.reshape(1, -1)
  j = j0.reshape(-1, 1) + j1.reshape(1, -1)

  k = np.repeat(np.arange(C), field_height * field_width).reshape(-1, 1)

  return (k, i, j)


def get_im2col_indices(x_shape, field_height, field_width, padding=1, stride=1):
    # First figure out what the size of the output should be
    N, H, W, C = x_shape
    assert (H + 2 * padding - field_height) % stride == 0
    assert (W + 2 * padding - field_height) % stride == 0
    out_height = (H + 2 * padding - field_height) // stride + 1
    out_width = (W + 2 * padding - field_width) // stride + 1

    i0 = np.repeat(np.arange(field_height), field_width)
    i0 = np.tile(i0, C)
    i1 = stride * np.repeat(np.arange(out_height), out_width)
    j0 = np.tile(np.arange(field_width), field_height * C)
    j1 = stride * np.tile(np.arange(out_width), out_height)
    # Row indices in padded input image
    i = i0.reshape(-1, 1) + i1.reshape(1, -1)
    # Column indices in padded input image
    j = j0.reshape(-1, 1) + j1.reshape(1, -1)

    k = np.repeat(np.arange(C), field_height * field_width).reshape(-1, 1)

    return k, i, j


def im2col_indices(x, field_height, field_width, padding=1, stride=1):
    """ An implementation of im2col based on some fancy indexing """
    # Zero-pad the input
    p = padding
    x_padded = np.pad(x, ((0, 0), (p, p), (p, p), (0, 0)), mode="constant")

    # Compute indices in input image x, taking padding and stride into account.
    # k will be the channels to slice, and i and j will be the spatial position
    k, i, j = get_im2col_indices(x.shape, field_height, field_width, padding, stride)

    # Obtain values at index positions
    cols = x_padded[:, i, j, k]
    # Number of input channels C
    C = x.shape[3]
    # Reshape to output size (kernel_size * number of channels), which is the number of pixels under one filter kernel, times the number of times to apply the kernel
    cols = cols.transpose(0, 2, 1).reshape(-1, field_height * field_width * C).T
    return cols


def im2col_indices_org(x, field_height, field_width, padding=1, stride=1):
    """ An implementation of im2col based on some fancy indexing """
    # Zero-pad the input
    p = padding
    x_padded = np.pad(x, ((0, 0), (0, 0), (p, p), (p, p)), mode='constant')

    # Compute indices in input image x, taking padding and stride into account.
    # k will be the channels to slice, and i and j will be the spatial position
    k, i, j = get_im2col_indices_org(x.shape, field_height, field_width, padding, stride)

    # Obtain values at index positions
    cols = x_padded[:, k, i, j]
    # Number of input channels C
    C = x.shape[1]
    # Reshape to output size (kernel_size * number of channels), which is the number of pixels under one filter kernel, times the number of times to apply the kernel
    cols = cols.transpose(1, 2, 0).reshape(field_height * field_width * C, -1)
    return cols


def col2im_indices_org(cols, x_shape, field_height=3, field_width=3, padding=1, stride=1):
    """ An implementation of col2im based on fancy indexing and np.add.at """
    N, C, H, W = x_shape
    H_padded, W_padded = H + 2 * padding, W + 2 * padding
    x_padded = np.zeros((N, C, H_padded, W_padded), dtype=cols.dtype)
    k, i, j = get_im2col_indices_org(x_shape, field_height, field_width, padding, stride)
    cols_reshaped = cols.reshape(C * field_height * field_width, -1, N)
    cols_reshaped = cols_reshaped.transpose(2, 0, 1)
    np.add.at(x_padded, (slice(None), k, i, j), cols_reshaped)
    if padding == 0:
        return x_padded
    return x_padded[:, :, padding:-padding, padding:-padding]


def test_conv():
    num_samples = 1
    num_channels = 3
    spatial_size = 3
    x1 = np.arange(num_samples * num_channels * spatial_size * spatial_size).reshape(
        (num_samples, num_channels, spatial_size, spatial_size))
    x2 = x1.transpose((0, 2, 3, 1))
    kernel_size = 3
    stride = 1
    padding = 0
    x1_col = im2col_indices_org(x1, kernel_size, kernel_size, padding=padding, stride=stride)
    x2_col = im2col_indices(x2, kernel_size, kernel_size, padding=padding, stride=stride)
    print(np.allclose(x1_col, x2_col))

    num_kernels = 1
    weights = np.arange(num_kernels * kernel_size * kernel_size * num_channels).reshape(
        (num_channels, num_kernels, kernel_size, kernel_size))
    weights_col = weights.transpose(2, 3, 0, 1).reshape(num_kernels, -1)
    result = weights_col @ x2_col

    output_size = (spatial_size - kernel_size + 2 * padding) // stride + 1
    result_reshaped = result.reshape(num_kernels, output_size, output_size, num_samples).transpose(3, 1, 2, 0)


def test_pool():
    n = 2
    d = 3
    h = 28
    w = 28
    # X = np.arange(n * d * h * w).reshape(n, d, h, w)
    X = np.random.randn(n, d, h, w)

    # Pooling layer parameters
    size = 4
    stride = 4
    h_out = (h - size) // stride + 1
    w_out = (w - size) // stride + 1

    # Let say our input X is 5x10x28x28
    # Our pooling parameter are: size = 2x2, stride = 2, padding = 0
    # i.e. result of 10 filters of 3x3 applied to 5 imgs of 28x28 with stride = 1 and padding = 1

    # First, reshape it to 50x1x28x28 to make im2col arranges it fully in column
    X_reshaped = X.reshape(n * d, 1, h, w)

    # The result will be 4x9800
    # Note if we apply im2col to our 5x10x28x28 input, the result won't be as nice: 40x980
    X_col = im2col_indices_org(X_reshaped, size, size, padding=0, stride=stride)

    # Next, at each possible patch location, i.e. at each column, we're taking the max index
    max_idx = np.argmax(X_col, axis=0)

    # Finally, we get all the max value at each column
    # The result will be 1x9800
    out = X_col[max_idx, range(max_idx.size)]

    # Reshape to the output size: 14x14x5x10
    out = out.reshape(h_out, w_out, n, d)

    # Transpose to get 5x10x14x14 output
    out = out.transpose(2, 3, 0, 1)

    # My pool
    my_X = X.transpose(0, 2, 3, 1)
    my_X_reshaped = my_X.transpose(0, 3, 1, 2).reshape(d * n, h, w, 1)
    my_X_col = im2col_indices(my_X_reshaped, size, size, padding=0, stride=stride)
    my_max_idx = np.argmax(my_X_col, axis=0)
    my_out = my_X_col[my_max_idx, range(my_max_idx.size)]
    my_out = my_out.reshape(n, d, h_out, w_out).transpose(0, 2, 3, 1)

    print(np.allclose(out.transpose(0, 2, 3, 1), my_out))


if __name__ == "__main__":
    test_pool()
