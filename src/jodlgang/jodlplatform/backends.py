from django.core.exceptions import PermissionDenied
from .utils import get_face_recognition_cnn
from .models import User
from PIL import Image
import numpy as np
import logging


logger = logging.getLogger(__name__)


class FaceAuthenticationBackend(object):
    def authenticate(self, request, **kwargs):
        if "face_img" not in kwargs:
            raise PermissionDenied

        # Check the token and return the user
        try:
            user = User.objects.get(email=kwargs["username"])
        except User.DoesNotExist:
            raise PermissionDenied

        try:
            face_img = np.array(Image.open(kwargs["face_img"])).astype(np.float)
            cnn = get_face_recognition_cnn()
            class_probabilities = cnn.inference(face_img[None, :])[0]
            # TODO special handling for numpy exceptions
            most_likely_class = np.argmax(class_probabilities)
            if class_probabilities[most_likely_class] <= 0.5:
                raise PermissionDenied

            if user.id == most_likely_class:
                return user
        except Exception as e:
            logger.error("Exception in face recognition: " + str(e))
            raise PermissionDenied

    def get_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return None
