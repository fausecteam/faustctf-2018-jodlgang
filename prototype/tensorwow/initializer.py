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
