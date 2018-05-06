from .utils import get_face_recognition_cnn
from .models import User
from PIL import Image
import numpy as np
import os


class FaceAuthenticationBackend(object):
    def authenticate(self, request, **kwargs):
        if "face_img" not in kwargs:
            # TODO Deny access immediately
            return None

        # Check the token and return the user
        try:
            user = User.objects.get(email=kwargs["username"])
            face_img = np.array(Image.open(kwargs["face_img"])).astype(np.float)
            cnn = get_face_recognition_cnn()
            class_probabilities = cnn.inference(face_img[None, :])[0]

            if user.check_password(kwargs["password"]):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return None
