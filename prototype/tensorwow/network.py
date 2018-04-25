class Network(object):
    def __init__(self, loss_func):
        self._loss_func = loss_func

        self._layers = []

    def add_layer(self, layer):
        # Check compatibility
        if len(self._layers) > 0:
            assert self._layers[-1].num_output_units == layer.num_input_units, "Dimensions do not match"

        self._layers.append(layer)

    def inference(self, inputs):
        # Compute forward pass
        input_neurons = inputs
        for layer in self._layers:
            input_neurons = layer.forward(input_neurons)
        return input_neurons

    def train(self, inputs, targets, learning_rate):
        # Compute forward pass
        input_neurons = inputs
        for layer in self._layers:
            input_neurons = layer.forward(input_neurons)

        # Compute loss
        loss = self._loss_func.compute(input_neurons, targets)

        # Compute derivative of loss function
        dloss = self._loss_func.derivative(input_neurons, targets)
        upstream_gradient = dloss
        for layer in reversed(self._layers):
            upstream_gradient = layer.backward(upstream_gradient)

        for layer in self._layers:
            layer.update(learning_rate)

        return loss
