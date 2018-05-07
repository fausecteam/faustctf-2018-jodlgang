import numpy as np


class RectifiedLinearUnit(object):
    def __init__(self):
        pass

    def compute(self, x):
        return np.maximum(x, 0, x)

    def derivative(self, x, partial_derivative_idx=None):
        dx = np.zeros_like(x)

        if partial_derivative_idx is None:
            dx[x > 0] = 1
            return dx
        else:
            dx[x[:, partial_derivative_idx] > 0, partial_derivative_idx] = 1
            return dx


class Softmax(object):
    def __init__(self):
        pass

    def compute(self, x):
        exps = np.exp(x)
        return exps / np.sum(exps, axis=1)[:, None]

    def derivative(self, x, partial_derivative_idx=None):
        """
        Computes the derivative w.r.t. softmax input z_i
        :param x:
        :param i: index
        :return:
        """
        ps = self.compute(x)
        if partial_derivative_idx is None:
            # Compute derivative
            return ps * (1.0 - ps)

        p_i = ps[:, partial_derivative_idx]
        res = -p_i[:, None] * ps
        res[:, partial_derivative_idx] = p_i * (1.0 - p_i)
        return res
