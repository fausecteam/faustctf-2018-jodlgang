import numpy as np


class LinearUnit(object):
    def __init__(self):
        pass

    def compute(self, x):
        return x

    def derivative(self, x, partial_derivative_idx=None):
        # TODO double check
        if partial_derivative_idx is None:
            return np.ones_like(x)
        else:
            dx = np.zeros_like(x)
            dx[partial_derivative_idx] = 1
            return dx


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


class MeanSquaredError(object):
    def __init__(self):
        pass

    def compute(self, outputs, targets):
        return np.mean(0.5 * np.sum(np.square(outputs - targets), axis=1))

    def derivative(self, outputs, targets):
        num_samples = len(outputs)
        return (outputs - targets) / num_samples


class CategoricalCrossEntropyWithSoftmaxLoss(object):
    def __init__(self):
        pass

    def compute(self, outputs, targets):
        return np.mean(-np.sum(targets * np.log(outputs), axis=1))

    def derivative(self, outputs, targets):
        num_samples = len(outputs)
        return (targets - outputs) / num_samples


class LogLikelihoodLoss(object):
    def __init__(self):
        pass

    def compute(self, outputs, targets):
        return np.mean(-np.sum(targets * np.log(outputs), axis=1))

    def derivative(self, outputs, targets):
        num_samples = len(outputs)
        # Target is one-hot encoded vector
        d = np.zeros_like(outputs)
        targets_mask = np.where(targets == 1)
        d[targets_mask] = -1 / outputs[targets_mask]
        return d / num_samples
