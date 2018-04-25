import tensorflow as tf
from layers import ConvLayer
from functions import LinearUnit
from initializer import ConstantInitializer
import numpy as np


num_samples = 5
num_channels = 3
spatial_size = 5
kernel_size = 3
num_filters = 5

input_placeholder = tf.placeholder(tf.float32, [None, spatial_size, spatial_size, num_channels])
tf_conv_weights = tf.get_variable("weights", shape=[kernel_size, kernel_size, num_channels, num_filters], initializer=tf.contrib.layers.xavier_initializer())
tf_conv_layer = tf.nn.conv2d(input_placeholder, tf_conv_weights, strides=[1, 1, 1, 1], padding="SAME")

# input_imgs = np.random.randn(num_samples, spatial_size, spatial_size, input_channels)
input_imgs = np.arange(num_samples * num_channels * spatial_size * spatial_size).reshape((num_samples, spatial_size, spatial_size, num_channels))
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    feed_dict = {input_placeholder: input_imgs}
    tf_conv_output, conv_weights = sess.run([tf_conv_layer, tf_conv_weights], feed_dict=feed_dict)


my_conv_layer = ConvLayer(kernel_size, num_channels, num_filters, LinearUnit(), ConstantInitializer(0), ConstantInitializer(0), padding=1)
my_conv_layer._weights = conv_weights
my_conv_layer_output = my_conv_layer.forward(input_imgs)

print(np.allclose(tf_conv_output, my_conv_layer_output))
