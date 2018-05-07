import sys

import os

old = list(sys.path)
SERVER_DIR = '../../src/jodlgang/'
sys.path.append(SERVER_DIR)

from tensorwow.model import FaceRecognitionCNN

def get_face_recognition_cnn(weights_file):
    if weights_file is None or not os.path.exists(weights_file):
        raise ValueError("Weights for face recognition CNN could not be found")

    cnn = FaceRecognitionCNN()
    cnn.restore_weights(weights_file)
    return cnn

sys.path = old # restore the path