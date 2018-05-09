from tensorwow.model import FaceRecognitionCNN
from jodlplatform import face_recognition_cnn
from django.conf import settings
import numpy as np
import os


def get_face_recognition_cnn():
    global face_recognition_cnn
    if face_recognition_cnn is None:
        np.seterr(all="raise")
        # Set up face recognition CNN
        weights_file = getattr(settings, "CNN_WEIGHTS", None)
        if weights_file is None or not os.path.exists(weights_file):
            raise ValueError("Weights for face recognition CNN could not be found")

        face_recognition_cnn = FaceRecognitionCNN()
        face_recognition_cnn.restore_weights(weights_file)

    return face_recognition_cnn
