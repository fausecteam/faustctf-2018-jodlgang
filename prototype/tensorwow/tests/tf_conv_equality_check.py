import tensorflow as tf
from tensorwow.layers import ConvLayer
from tensorwow.functions import LinearUnit
from tensorwow.initializer import ConstantInitializer
import numpy as np


def conv_forward_strides(x, w, b, padding, stride):
    N, C, H, W = x.shape
    F, _, HH, WW = w.shape

    # Check dimensions
    assert (W + 2 * padding - WW) % stride == 0, 'width does not work'
    assert (H + 2 * padding - HH) % stride == 0, 'height does not work'

    # Pad the input
    p = padding
    x_padded = np.pad(x, ((0, 0), (0, 0), (p, p), (p, p)), mode='constant')

    # Figure out output dimensions
    H += 2 * padding
    W += 2 * padding
    out_h = (H - HH) // stride + 1
    out_w = (W - WW) // stride + 1

    # Perform an im2col operation by picking clever strides
    shape = (C, HH, WW, N, out_h, out_w)
    strides = (H * W, W, 1, C * H * W, stride * W, stride)
    strides = x.itemsize * np.array(strides)
    x_stride = np.lib.stride_tricks.as_strided(x_padded,
                                               shape=shape, strides=strides)
    x_cols = np.ascontiguousarray(x_stride)
    x_cols.shape = (C * HH * WW, N * out_h * out_w)

    # Now all our convolutions are a big matrix multiply
    res = w.reshape(F, -1).dot(x_cols) + b.reshape(-1, 1)

    # Reshape the output
    res.shape = (F, N, out_h, out_w)
    out = res.transpose(1, 0, 2, 3)

    # Be nice and return a contiguous array
    # The old version of conv_forward_fast doesn't do this, so for a fair
    # comparison we won't either
    out = np.ascontiguousarray(out)

    return out


def conv_strides_wrapper(x, w, b):
    return conv_forward_strides(x.transpose(0, 3, 1, 2), w.transpose(3, 2, 0, 1), b, padding=1, stride=1).transpose(0, 2, 3, 1)


num_samples = 5
num_channels = 3
spatial_size = 224
kernel_size = 3
num_filters = 64

input_placeholder = tf.placeholder(tf.float32, [None, spatial_size, spatial_size, num_channels])
tf_conv_weights = tf.get_variable("weights", shape=[kernel_size, kernel_size, num_channels, num_filters], initializer=tf.contrib.layers.xavier_initializer())
tf_conv_layer = tf.nn.conv2d(input_placeholder, tf_conv_weights, strides=[1, 1, 1, 1], padding="SAME")

input_imgs = np.random.randn(num_samples, spatial_size, spatial_size, num_channels)
# input_imgs = np.arange(num_samples * num_channels * spatial_size * spatial_size).reshape((num_samples, spatial_size, spatial_size, num_channels))
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    feed_dict = {input_placeholder: input_imgs}
    tf_conv_output, conv_weights = sess.run([tf_conv_layer, tf_conv_weights], feed_dict=feed_dict)


my_conv_layer = ConvLayer(kernel_size, num_channels, num_filters, LinearUnit(), ConstantInitializer(0), ConstantInitializer(0), padding=1)
my_conv_layer._weights = conv_weights
my_conv_layer_output = my_conv_layer.forward(input_imgs)

strides_output = conv_strides_wrapper(input_imgs, conv_weights, my_conv_layer.bias)

print(np.allclose(tf_conv_output, my_conv_layer_output, rtol=1e-3))
print(np.allclose(tf_conv_output, strides_output, rtol=1e-3))


# Time comparison
import time
runs = 100
elapsed_seconds = time.time()
for _ in range(runs):
    my_conv_layer.forward(input_imgs)
elapsed_seconds = time.time() - elapsed_seconds
print("[im2col] Elapsed seconds: {:3.2f}".format(elapsed_seconds))

x_t = input_imgs.transpose(0, 3, 1, 2)
w_t = conv_weights.transpose(3, 2, 0, 1)
elapsed_seconds = time.time()
for _ in range(runs):
    conv_forward_strides(x_t, w_t, my_conv_layer.bias, padding=1, stride=1)
elapsed_seconds = time.time() - elapsed_seconds
print("[strides] Elapsed seconds: {:3.2f}".format(elapsed_seconds))
# strides method marginally faster
