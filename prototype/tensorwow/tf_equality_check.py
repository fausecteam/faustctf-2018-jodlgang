from .initializer import XavierInitializer, ConstantInitializer
from .functions import RectifiedLinearUnit, MeanSquaredError
from .layers import FullyConnectedLayer
from .network import Network
import tensorflow as tf
import numpy as np


np.random.seed(12345)

# Build my network
net = Network(MeanSquaredError())
fc0 = FullyConnectedLayer(2, 2, RectifiedLinearUnit(), XavierInitializer(), ConstantInitializer(0.1))
fc1 = FullyConnectedLayer(2, 1, RectifiedLinearUnit(), XavierInitializer(), ConstantInitializer(0.1))
net.add_layer(fc0)
net.add_layer(fc1)

# Set up the weights in TensorFlow
tf_fc0_weights = tf.Variable(np.copy(fc0.weights), dtype=tf.float32, name="fc0_weights")
tf_fc0_bias = tf.Variable(np.copy(fc0.bias), dtype=tf.float32, name="fc0_bias")
tf_fc1_weights = tf.Variable(np.copy(fc1.weights), dtype=tf.float32, name="fc1_weights")
tf_fc1_bias = tf.Variable(np.copy(fc1.bias), dtype=tf.float32, name="fc1_bias")
input_placeholder = tf.placeholder(tf.float32, [None, 2])
target_placeholder = tf.placeholder(tf.float32, [None, 1])

# Set up TensorFlow network
tf_fc0_z = tf.matmul(input_placeholder, tf_fc0_weights) + tf_fc0_bias
tf_fc0_a = tf.nn.relu(tf_fc0_z)
tf_fc1_z = tf.matmul(tf_fc0_a, tf_fc1_weights) + tf_fc1_bias
tf_fc1_a = tf.nn.relu(tf_fc1_z)
temp_var = tf.Variable(np.zeros((4, 1), dtype=np.float32), dtype=tf.float32, name="temp")


# Make it learn the and function
inputs = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
], dtype=np.float32)

targets = np.array([
    [0],
    [0],
    [0],
    [1]
], dtype=np.float32)

learning_rate = 0.01

# Evaluate TensorFlow network
assign_op = temp_var.assign(tf_fc1_z)
tf_loss = tf.reduce_mean(0.5 * tf.reduce_sum(tf.square(tf_fc1_a - target_placeholder), axis=1))
optimizer = tf.train.GradientDescentOptimizer(learning_rate)
grads_and_vars = optimizer.compute_gradients(tf_loss)
train_op = optimizer.minimize(tf_loss)
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    feed_dict = {input_placeholder: inputs, target_placeholder: targets}
    # Was for debugging purposes
    sess.run(assign_op, feed_dict=feed_dict)
    tf_loss_val = sess.run(tf_loss, feed_dict=feed_dict)

    outputs = net.inference(inputs)

    # Print the gradients w.r.t. each variable
    for gv in grads_and_vars:
        grad_tensor, var_tensor = gv
        if grad_tensor is None:
            continue
        grad_tensor_val, var_tensor_val = sess.run(gv, feed_dict=feed_dict)
        print(var_tensor.name)
        print(var_tensor_val)
        print(grad_tensor.name)
        print(grad_tensor_val)
        print("")

    # Take one training step
    sess.run(train_op, feed_dict=feed_dict)

    loss_val = net.train(inputs, targets, learning_rate=learning_rate)

    assert np.allclose(tf_loss_val, loss_val)

    # Now check for equivalence
    assert np.allclose(sess.run(tf_fc0_weights), fc0.weights)
    assert np.allclose(sess.run(tf_fc0_bias), fc0.bias)
    assert np.allclose(sess.run(tf_fc1_weights), fc1.weights)
    assert np.allclose(sess.run(tf_fc1_bias), fc1.bias)
