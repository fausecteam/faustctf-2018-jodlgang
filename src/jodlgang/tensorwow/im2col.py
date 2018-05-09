import numpy as np


cache = dict()


def get_im2col_indices_with_cache(x_shape, field_height, field_width, padding, stride):
    key = (x_shape, field_height, field_width, padding, stride)
    if key in cache:
        return cache[key]

    indices = get_im2col_indices(x_shape, field_height, field_width, padding, stride)
    cache[key] = indices
    return indices


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
    k, i, j = get_im2col_indices_with_cache(x.shape, field_height, field_width, padding, stride)

    # Obtain values at index positions
    cols = x_padded[:, i, j, k]
    # Number of input channels C
    C = x.shape[3]
    # Reshape to output size (kernel_size * number of channels), which is the number of pixels under one filter kernel, times the number of times to apply the kernel
    cols = cols.transpose(0, 2, 1).reshape(-1, field_height * field_width * C).T
    return cols
