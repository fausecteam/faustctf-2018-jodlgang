from os.path import join

import os
from ..path_utils import ExtraLoadPaths, SERVER_DIR

with ExtraLoadPaths(SERVER_DIR):
    from tensorwow import model
    from tensorwow import layers
    from tensorwow import initializer
    from tensorwow import functions
    from tensorwow import im2col


def get_face_recognition_cnn(weights_file):
    if weights_file is None or not os.path.exists(weights_file):
        raise ValueError("Weights for face recognition CNN could not be found")

    cnn = model.FaceRecognitionCNN()
    cnn.restore_weights(weights_file)
    return cnn



