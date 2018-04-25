import numpy as np
cimport numpy as np
cimport cython


# Make methods compatible to both float32 and float64 dtypes
ctypedef fused DTYPE_t:
    np.float32_t
    np.float64_t


@cython.boundscheck(False)
def im2col_cython(np.ndarray[DTYPE_t, ndim=4] x, int kernel_height, int kernel_width, int padding, int stride):
    cdef int num_samples = x.shape[0]
    cdef int height = x.shape[1]
    cdef int width = x.shape[2]
    cdef int channels = x.shape[3]

    cdef int output_height = (height - kernel_height + 2 * padding) // stride + 1
    cdef int output_width = (width - kernel_width + 2 * padding) // stride + 1

    # Pad input
    cdef np.ndarray[DTYPE_t, ndim=4] x_padded = np.pad(x, ((0, 0), (padding, padding), (padding, padding), (0, 0)), mode="constant")

    # Allocate output
    cdef np.ndarray[DTYPE_t, ndim=2] x_cols = np.zeros((channels * kernel_height * kernel_width, num_samples * output_height * output_width), dtype=x.dtype)

    # Inner loop
    for c in range(channels):
        for yy in range(output_height):
            for xx in range(output_width):
                for jj in range(kernel_height):
                    for ii in range(kernel_width):
                        row = (c * kernel_width + jj) * kernel_height + ii
                        for i in range(num_samples):
                            #col = (yy * output_width + xx) * num_samples + i
                            col = (i * output_height + yy) * output_width + xx
                            x_cols[row, col] = x_padded[i, stride * yy + jj, stride * xx + ii, c]

    return x_cols
