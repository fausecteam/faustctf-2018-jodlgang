import tensorflow as tf


def conv2d_relu(x, filters, name):
    with tf.variable_scope(name):
        weights = weights_variable_truncated_normal([3, 3, x.shape[3].value, filters], mean=0, stddev=1e-2, name=name + "_weights")
        bias = bias_variable([filters], value=0, name=name + "_bias")
        z = conv2d(x, weights) + bias
        a = tf.nn.relu(z)
        return a


def conv2d(x, W):
    """
    Returns a 2D convolutional layer with full stride.
    """
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding="SAME")


def max_pool_2x2(x):
    """
    Mapping over 2x2 blocks
    """
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")


def weights_variable_truncated_normal(shape, mean=0.0, stddev=0.1, name=None, trainable=True):
    """
    Creates a weight matrix of given shape with uniform weights
    :param shape: shape of weight matrix
    :param mean: Mean of the truncated normal distribution
    :param stddev: Standard deviation of the truncated normal distribution
    :param name: Optional name for the variable. Defaults to `'Variable'` and gets
        uniquified automatically.
    :param trainable: If `True`, the default, also adds the variable to the graph
        collection `GraphKeys.TRAINABLE_VARIABLES`. This collection is used as
        the default list of variables to use by the `Optimizer` classes.
    :return: Weight matrix
    """
    initial = tf.truncated_normal(shape, mean=mean, stddev=stddev)
    return tf.get_variable(name, trainable=trainable, initializer=initial)


def weights_variable_xavier(shape, name, trainable=True):
    """
    Creates a weight matrix of given shape with xavier weights.
    Note that the xavier initializer is the same as the glorot_uniform_initializer.
    :param shape: shape of weight matrix
    :param name: name of the variable
    :param trainable: If `True`, the default, also adds the variable to the graph
        collection `GraphKeys.TRAINABLE_VARIABLES`. This collection is used as
        the default list of variables to use by the `Optimizer` classes.
    :return: Weight matrix
    """
    return tf.get_variable(name, shape=shape, initializer=tf.contrib.layers.xavier_initializer(), trainable=trainable)


def bias_variable(shape, value=0, name=None, trainable=True):
    """
    Creates a vector of given shape with 0 initial values
    :param shape: shape of vector
    :param value: A constant value
    :param name: Optional name for the variable. Defaults to `'Variable'` and gets
        uniquified automatically.
    :param trainable: If `True`, the default, also adds the variable to the graph
        collection `GraphKeys.TRAINABLE_VARIABLES`. This collection is used as
        the default list of variables to use by the `Optimizer` classes.
    :return: Bias vector
    """
    initial = tf.constant(value, shape=shape, dtype=tf.float32)
    return tf.get_variable(name, trainable=trainable, initializer=initial)
