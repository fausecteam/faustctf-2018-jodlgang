from tensorwow.initializer import ConstantInitializer, TruncatedNormalInitializer
from tensorwow.layers import ConvLayer, FullyConnectedLayer, MaxPoolLayer
from tensorwow.functions import RectifiedLinearUnit, Softmax
from collections import OrderedDict
import numpy as np
import h5py


class FaceRecognitionCNN(object):
    def __init__(self):
        self._input_height = 224
        self._input_width = 224
        self._input_channels = 3

        # Set up model

        # Block 1
        # (224, 224, 3) -> (112, 112, 64)
        conv1_1 = ConvLayer(3, self._input_channels, 64, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv1_2 = ConvLayer(3, 64, 64, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        pool1 = MaxPoolLayer(2, padding=0, stride=2)

        # Block 2
        # (112, 112, 64) -> (56, 56, 128)
        conv2_1 = ConvLayer(3, 64, 128, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv2_2 = ConvLayer(3, 128, 128, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        pool2 = MaxPoolLayer(2, padding=0, stride=2)

        # Block 3
        # (56, 56, 128) -> (28, 28, 256)
        conv3_1 = ConvLayer(3, 128, 256, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv3_2 = ConvLayer(3, 256, 256, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv3_3 = ConvLayer(3, 256, 256, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        pool3 = MaxPoolLayer(2, padding=0, stride=2)

        # Block 4
        # (28, 28, 256) -> (14, 14, 512)
        conv4_1 = ConvLayer(3, 256, 512, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv4_2 = ConvLayer(3, 512, 512, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv4_3 = ConvLayer(3, 512, 512, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        pool4 = MaxPoolLayer(2, padding=0, stride=2)

        # Block 5
        # (14, 14, 512) -> (7, 7, 512)
        conv5_1 = ConvLayer(3, 512, 512, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv5_2 = ConvLayer(3, 512, 512, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        conv5_3 = ConvLayer(3, 512, 512, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        pool5 = MaxPoolLayer(2, padding=0, stride=2)

        fc6 = FullyConnectedLayer(7 * 7 * 512, 4096, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        fc7 = FullyConnectedLayer(4096, 4096, RectifiedLinearUnit(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))
        fc8 = FullyConnectedLayer(4096, 530, Softmax(), TruncatedNormalInitializer(mean=0, stddev=1e-2), ConstantInitializer(0))

        self._layers = OrderedDict([
            ("conv1_1", conv1_1),
            ("conv1_2", conv1_2),
            ("pool1", pool1),
            ("conv2_1", conv2_1),
            ("conv2_2", conv2_2),
            ("pool2", pool2),
            ("conv3_1", conv3_1),
            ("conv3_2", conv3_2),
            ("conv3_3", conv3_3),
            ("pool3", pool3),
            ("conv4_1", conv4_1),
            ("conv4_2", conv4_2),
            ("conv4_3", conv4_3),
            ("pool4", pool4),
            ("conv5_1", conv5_1),
            ("conv5_2", conv5_2),
            ("conv5_3", conv5_3),
            ("pool5", pool5),
            ("fc6", fc6),
            ("fc7", fc7),
            ("fc8", fc8),
        ])

    @property
    def input_height(self):
        return self._input_height

    @property
    def input_width(self):
        return self._input_width

    @property
    def input_channels(self):
        return self._input_channels

    def restore_weights(self, weights_file):
        with h5py.File(weights_file, "r") as f:
            all_datasets = list(f.keys())
            for dataset_name in all_datasets:
                layer = self._layers[dataset_name]
                dataset = f[dataset_name]

                for key in list(dataset.keys()):
                    if "weights" in key:
                        layer.weights = dataset[key].value
                    elif "bias" in key:
                        layer.bias = dataset[key].value
                    else:
                        raise ValueError("Key not known")

    @staticmethod
    def preprocess(images):
        if not len(images.shape) == 4:
            raise ValueError("Expected four-dimensional input")

        preprocessed_imgs = np.copy(images)
        preprocessed_imgs = preprocessed_imgs[..., ::-1]
        preprocessed_imgs[..., 0] -= 93.5940
        preprocessed_imgs[..., 1] -= 104.7624
        preprocessed_imgs[..., 2] -= 129.1863
        return preprocessed_imgs

    def inference(self, images):
        if not len(images.shape) == 4:
            raise ValueError("Expected four-dimensional input")
        if images.shape[1] != self._input_height or images.shape[2] != self._input_width or images.shape[3] != self._input_channels:
            raise ValueError("Invalid dimensions")

        x = self.preprocess(images)
        # Forward pass
        for name, layer in self._layers.items():
            x = layer.forward(x)

            # Flatten activations when transitioning from convolutional cascade to fully-connected layers
            if name == "pool5":
                num_samples = x.shape[0]
                x = x.reshape(num_samples, -1)

        # Return class probabilities after softmax activation
        return x
