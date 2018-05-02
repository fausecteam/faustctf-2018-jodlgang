import numpy as np
from tensorwow.im2col import im2col_indices


class FullyConnectedLayer(object):
    def __init__(self, num_input_units, num_output_units, activation_func, weights_initializer, bias_initializer):
        """

        :param num_input_units: Number of input dimensions D
        :param num_output_units: Number of output dimensions O
        :param activation_func: Activation function
        :param weights_initializer: Weights initializer
        :param bias_initializer: Bias initializer
        """
        self._num_input_units = num_input_units
        self._num_output_units = num_output_units
        self._activation_func = activation_func

        self._weights = weights_initializer.initialize((num_input_units, num_output_units))
        self._bias = bias_initializer.initialize((num_output_units))

        self._x = None
        self._z = None
        self._a = None
        self._dw = None
        self._db = None

    @property
    def num_input_units(self):
        return self._num_input_units

    @property
    def num_output_units(self):
        return self._num_output_units

    @property
    def weights(self):
        """
        :return: D x M matrix
        """
        return self._weights

    @weights.setter
    def weights(self, weights):
        if weights.shape != (self._num_input_units, self._num_output_units):
            raise ValueError("Invalid dimensions")

        self._weights = weights

    @property
    def bias(self):
        """
        :return: vector of length M
        """
        return self._bias

    @bias.setter
    def bias(self, bias):
        if bias.shape != (self._num_output_units,):
            raise ValueError("Invalid dimensions")

        self._bias = bias

    def forward(self, x):
        """

        :param x: N x D matrix
        :return: N x M matrix
        """
        assert len(x.shape) == 2, "Inputs must be a two-dimensional tensor"
        assert x.shape[1] == self._num_input_units, "Inputs does not match input size"

        z = np.dot(x, self._weights) + self._bias
        a = self._activation_func.compute(z)

        # Cache values for backward step
        self._x = x
        self._z = z
        self._a = a

        return a

    def backward(self, upstream_gradient):
        """

        :param upstream_gradient: N x M matrix
        :return: derivative w.r.t. the inputs, matrix of shape N x D
        """
        num_samples, len_upstream_gradient = upstream_gradient.shape
        assert len_upstream_gradient == self._num_output_units

        # Backpropagate through activation function
        # Unfortunately the softmax derivative is position-dependent
        dz = np.zeros_like(upstream_gradient)
        for o in range(self.num_output_units):
            activation_func_derivative = self._activation_func.derivative(self._z, o)
            dz[:, o] = np.sum(upstream_gradient * activation_func_derivative, axis=1)

        # dz = upstream_gradient * self._activation_func.derivative(self._z)

        # Compute derivative w.r.t. weights
        dw = np.dot(self._x.T, dz)

        # Compute the derivative w.r.t. bias b
        db = np.sum(dz, axis=0)

        # Compute the derivative w.r.t. the inputs x
        dx = np.dot(dz, self._weights.T)

        self._dw = dw
        self._db = db

        return dx

    def _backward_naive(self, upstream_gradient):
        """

        :param upstream_gradient: N x M matrix
        :return: derivative w.r.t. the inputs, matrix of shape N x D
        """
        num_samples, len_upstream_gradient = upstream_gradient.shape
        assert len_upstream_gradient == self._num_output_units

        # Undo activation function
        dz = upstream_gradient * self._activation_func.derivative(self._z)

        # Compute derivative w.r.t. weights w_io
        dw = np.zeros_like(self._weights)
        for i in range(self._num_input_units):
            for o in range(self._num_output_units):
                dw[i, o] = np.sum(dz[:, o] * self._x[:, i])
        assert np.allclose(np.dot(self._x.T, dz), dw)

        # Compute the derivative w.r.t. bias b_o
        db = np.zeros_like(self._bias)
        for o in range(self._num_output_units):
            db[o] = np.sum(dz[:, o])
        assert np.allclose(np.sum(dz, axis=0), db)

        # Compute the derivative w.r.t. the inputs x
        dx = np.zeros_like(self._x)
        for s in range(num_samples):
            for i in range(self._num_input_units):
                dx[s, i] = np.sum(dz[s, :] * self._weights[i, :])
        assert np.allclose(np.dot(dz, self._weights.T), dx)

        self._dw = dw
        self._db = db

        return dx

    def update(self, step_size):
        self._weights = self._weights - step_size * self._dw
        self._bias = self._bias - step_size * self._db


class ConvLayer(object):
    def __init__(self, kernel_size, num_input_channels, num_filters, activation_func, weights_initializer, bias_initializer, stride=1, padding=1):
        self._kernel_size = kernel_size
        self._num_input_channels = num_input_channels
        self._num_filters = num_filters
        self._padding = padding
        self._stride = stride
        self._activation_func = activation_func

        self._weights = weights_initializer.initialize((kernel_size, kernel_size, num_input_channels, num_filters))
        self._bias = bias_initializer.initialize((num_filters, 1))

    @property
    def weights(self):
        """
        :return: Weight matrix of shape (kernel_size, kernel_size, num_input_channels, num_filters)
        """
        return self._weights

    @property
    def bias(self):
        """
        :return: Bias vector of length num_filters
        """
        return self._bias

    @weights.setter
    def weights(self, weights):
        if weights.shape != (self._kernel_size, self._kernel_size, self._num_input_channels, self._num_filters):
            raise ValueError("Invalid dimensions")

        self._weights = weights

    @bias.setter
    def bias(self, bias):
        if bias.shape != (self._num_filters,):
            raise ValueError("Invalid dimensions")

        self._bias = bias

    def forward(self, x):
        """
        Computes the correlation of each input sample with the layer's kernel matrix
        :param x: input images of shape [num_samples, height, width, input_channels]
        :return: feature maps of shape [num_samples, height, width, num_filters]
        """
        assert len(x.shape) == 4, "Inputs must be a three-dimensional tensor"
        assert x.shape[3] == self._num_input_channels, "Inputs does not match required input channels"

        num_samples, height, width, channels = x.shape
        assert (height - self._kernel_size + 2 * self._padding) % self._stride == 0, "Invalid dimensions"
        assert (width - self._kernel_size + 2 * self._padding) % self._stride == 0, "Invalid dimensions"

        output_height = (height - self._kernel_size + 2 * self._padding) // self._stride + 1
        output_width = (width - self._kernel_size + 2 * self._padding) // self._stride + 1

        x_col = im2col_indices(x, self._kernel_size, self._kernel_size, padding=self._padding, stride=self._stride)
        # Move filter kernels to the front before reshaping to [num_filters, ...]
        # To make the filter matrix appear for each channel contiguously, move the channels dimension to the front as well
        weights_col = self._weights.transpose(3, 2, 0, 1).reshape(self._num_filters, -1)

        z = np.dot(weights_col, x_col) + self._bias[:, None]
        a = self._activation_func.compute(z)
        # Found this order through experimenting
        a = a.reshape(self._num_filters, num_samples, output_height, output_width).transpose(1, 2, 3, 0)

        return a

    def backward(self, upstream_gradient):
        raise NotImplementedError()


class MaxPoolLayer(object):
    def __init__(self, window_size, padding, stride):
        self._window_size = window_size
        self._padding = padding
        self._stride = stride

    def forward(self, x):
        num_samples, height, width, num_channels = x.shape
        assert (height - self._window_size) % self._stride == 0, "Invalid dimensions"
        assert (width - self._window_size) % self._stride == 0, "Invalid dimensions"
        output_height = (height - self._window_size) // self._stride + 1
        output_width = (width - self._window_size) // self._stride + 1

        x_prep = x.transpose(0, 3, 1, 2).reshape(num_samples * num_channels, height, width, 1)
        x_col = im2col_indices(x_prep, self._window_size, self._window_size, padding=self._padding, stride=self._stride)
        max_indices = np.argmax(x_col, axis=0)
        z = x_col[max_indices, range(len(max_indices))]
        z = z.reshape(num_samples, num_channels, output_height, output_width).transpose(0, 2, 3, 1)

        return z

    def backward(self, upstream_gradient):
        raise NotImplementedError()
