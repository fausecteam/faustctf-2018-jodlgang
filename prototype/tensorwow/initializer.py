import scipy.stats as stats
import numpy as np


class XavierInitializer(object):
    def __init__(self):
        pass

    def initialize(self, size):
        limit = np.sqrt(6 / np.prod(size))
        return np.random.uniform(-limit, limit, size).astype(np.float)


class ConstantInitializer(object):
    def __init__(self, constant):
        self._constant = constant

    def initialize(self, size):
        return self._constant * np.ones(size, dtype=np.float)


class TruncatedNormalInitializer(object):
    def __init__(self, mean, stddev):
        self._mean = mean
        self._stddev = stddev

    def initialize(self, size):
        return stats.truncnorm(-2, +2, loc=self._mean, scale=self._stddev)\
            .rvs(np.prod(size))\
            .reshape(size)
