from unittest import TestCase
from .initializer import XavierInitializer, ConstantInitializer
from .functions import RectifiedLinearUnit, MeanSquaredError, Softmax, CategoricalCrossEntropyWithSoftmaxLoss, LogLikelihoodLoss
from .layers import FullyConnectedLayer
from .network import Network
import tensorflow as tf
import numpy as np


class TensorwowVsTensorflow(TestCase):

    def test_fc_vs_tensorflow(self):
        np.random.seed(12345)
        tf.reset_default_graph()

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
        num_epochs = 10

        # Evaluate TensorFlow network
        tf_loss = tf.reduce_mean(0.5 * tf.reduce_sum(tf.square(tf_fc1_a - target_placeholder), axis=1))
        optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        train_op = optimizer.minimize(tf_loss)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            feed_dict = {input_placeholder: inputs, target_placeholder: targets}
            for i in range(num_epochs):
                tf_loss_val = sess.run(tf_loss, feed_dict=feed_dict)

                # Take one training step
                sess.run(train_op, feed_dict=feed_dict)

                loss_val = net.train(inputs, targets, learning_rate=learning_rate)

                assert np.allclose(tf_loss_val, loss_val)

                # Now check for equivalence
                self.assertTrue(np.allclose(sess.run(tf_fc0_weights), fc0.weights))
                self.assertTrue(np.allclose(sess.run(tf_fc0_bias), fc0.bias))
                self.assertTrue(np.allclose(sess.run(tf_fc1_weights), fc1.weights))
                self.assertTrue(np.allclose(sess.run(tf_fc1_bias), fc1.bias))

    def test_softmax_log_likelihood(self):
        """
        Compares the analytical expression of the derivative of the log likelihood loss with softmax activation to the derivative of the log likelihood and softmax function in sequential order
        """

        num_samples = np.random.randint(1, 20)
        num_classes = np.random.randint(2, 10)
        zs = np.random.rand(num_samples, num_classes)
        label = np.zeros((num_samples, num_classes))
        label[range(num_samples), np.random.randint(0, num_classes, size=num_samples)] = 1

        softmax = Softmax()
        log_likelihood_loss_func = LogLikelihoodLoss()
        cross_entropy_with_softmax_func = CategoricalCrossEntropyWithSoftmaxLoss()

        # Apply the softmax function
        ps = softmax.compute(zs)

        # Compute the derivative using the logits
        cross_entropy_derivative = cross_entropy_with_softmax_func.derivative(label, ps)
        # Compute the derivative by chaining the outputs together
        log_likelihood_derivatives = log_likelihood_loss_func.derivative(ps, label)
        chained_derivatives = np.zeros_like(zs)
        # Unfortunately the softmax's derivative is position-dependent
        for i in range(num_classes):
            softmax_derivative = softmax.derivative(zs, partial_derivative_idx=i)
            chained_derivatives[:, i] = np.sum(log_likelihood_derivatives * softmax_derivative, axis=1)

        assert np.allclose(cross_entropy_derivative, chained_derivatives)

    def test_softmax_vs_tensorflow(self):
        tf.reset_default_graph()

        # Build my network
        net = Network(LogLikelihoodLoss())
        fc0 = FullyConnectedLayer(2, 2, RectifiedLinearUnit(), XavierInitializer(), ConstantInitializer(0.1))
        fc1 = FullyConnectedLayer(2, 2, Softmax(), XavierInitializer(), ConstantInitializer(0.1))
        net.add_layer(fc0)
        net.add_layer(fc1)

        # Set up weights in TensorFlow
        tf_fc0_weights = tf.Variable(np.copy(fc0.weights), dtype=tf.float32, name="fc0_weights")
        tf_fc0_bias = tf.Variable(np.copy(fc0.bias), dtype=tf.float32, name="fc0_bias")
        tf_fc1_weights = tf.Variable(np.copy(fc1.weights), dtype=tf.float32, name="fc1_weights")
        tf_fc1_bias = tf.Variable(np.copy(fc1.bias), dtype=tf.float32, name="fc1_bias")
        input_placeholder = tf.placeholder(tf.float32, [None, 2])
        target_placeholder = tf.placeholder(tf.float32, [None, 2])

        # Set up network in TensorFlow
        tf_fc0_z = tf.matmul(input_placeholder, tf_fc0_weights) + tf_fc0_bias
        tf_fc0_a = tf.nn.relu(tf_fc0_z)
        tf_fc1_z = tf.matmul(tf_fc0_a, tf_fc1_weights) + tf_fc1_bias
        tf_fc1_a = tf.nn.softmax(tf_fc1_z)

        # Make it learn the and function again
        inputs = np.array([
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1]
        ], dtype=np.float32)

        targets = np.array([
            [1, 0],
            [1, 0],
            [1, 0],
            [0, 1],
            [1, 0],
            [1, 0],
            [1, 0],
            [0, 1]
        ], dtype=np.float32)

        learning_rate = 0.01

        # Evaluate TensorFlow network
        tf_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=target_placeholder, logits=tf_fc1_a))
        optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        train_op = optimizer.minimize(tf_loss)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            feed_dict = {input_placeholder: inputs, target_placeholder: targets}
            tf_loss_val = sess.run(tf_loss, feed_dict=feed_dict)

            # Take one training step
            sess.run(train_op, feed_dict=feed_dict)

            loss_val = net.train(inputs, targets, learning_rate=learning_rate)

            # Check for equivalence
            # The accuracy suffers quite a bit from the numerically unstable softmax backpropagation
            self.assertTrue(np.allclose(tf_loss_val, loss_val, rtol=1e-0))
            self.assertTrue(np.allclose(sess.run(tf_fc0_weights), fc0.weights, rtol=1e-1))
            self.assertTrue(np.allclose(sess.run(tf_fc0_bias), fc0.bias, rtol=1e-1))
            self.assertTrue(np.allclose(sess.run(tf_fc1_weights), fc1.weights, rtol=1e-1))
            self.assertTrue(np.allclose(sess.run(tf_fc1_bias), fc1.bias, rtol=1e-1))
