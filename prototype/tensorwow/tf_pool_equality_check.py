import tensorflow as tf
from layers import MaxPoolLayer
import numpy as np


num_samples = 10
input_channels = 2
input_height = 224
input_width = 224
stride = 1
window_size = 2

input_placeholder = tf.placeholder(tf.float32, [None, input_height, input_width, input_channels])
tf_pool_layer = tf.nn.max_pool(input_placeholder, ksize=[1, window_size, window_size, 1], strides=[1, stride, stride, 1], padding="VALID")

input_imgs = np.random.randn(num_samples, input_height, input_width, input_channels)
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    feed_dict = {input_placeholder: input_imgs}
    tf_pool_output = sess.run(tf_pool_layer, feed_dict=feed_dict)

my_pool_layer = MaxPoolLayer(window_size, padding=0, stride=stride)
my_pool_layer_output = my_pool_layer.forward(input_imgs)

print(np.allclose(my_pool_layer_output, tf_pool_output))
