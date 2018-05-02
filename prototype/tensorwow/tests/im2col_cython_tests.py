from tensorwow.im2col import im2col_indices
from tensorwow.im2col_cython import im2col_cython
import numpy as np
import time


num_samples = 20
height = 224
width = 224
channels = 3

kernel_size = 3
padding = 1
stride = 1

x = np.random.randn(num_samples, height, width, channels)
# x = np.arange(num_samples * height * width * channels, dtype=np.float).reshape((num_samples, channels, height, width)).transpose(0, 2, 3, 1)

num_tests = 1
elapsed_milliseconds = time.time()
for _ in range(num_tests):
    p_col = im2col_indices(x, kernel_size, kernel_size, padding, stride)
elapsed_milliseconds = time.time() - elapsed_milliseconds
print("[Python] Elapsed milliseconds: {:3.2f}".format(elapsed_milliseconds))

elapsed_milliseconds = time.time()
for _ in range(num_tests):
    c_col = im2col_cython(x, kernel_size, kernel_size, padding, stride)
elapsed_milliseconds = time.time() - elapsed_milliseconds
print("[Cython] Elapsed milliseconds: {:3.2f}".format(elapsed_milliseconds))

print(np.allclose(p_col, c_col))
