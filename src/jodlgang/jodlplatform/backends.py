from django.core.exceptions import PermissionDenied
from .utils import get_face_recognition_cnn
from .models import User
from PIL import Image
import numpy as np
import logging
import time


logger = logging.getLogger(__name__)


class FaceAuthenticationBackend(object):
    def authenticate(self, request, **kwargs):
        if 'face_img' not in request.FILES:
            raise PermissionDenied

        try:
            user = User.objects.get(email=kwargs["username"])
        except User.DoesNotExist:
            raise PermissionDenied

        logger.debug("Retrieving face recognition CNN")
        cnn = get_face_recognition_cnn()

        try:
            logger.debug("Converting image to numpy array")
            face_img = np.array(Image.open(request.FILES['face_img'])).astype(np.float)
        except Exception as e:
            logger.error("Exception in face recognition: {} ({})".format(str(e), type(e)))
            raise PermissionDenied

        if len(face_img.shape) != 3 or face_img.shape[0] != cnn.input_height or face_img.shape[1] != cnn.input_width or face_img.shape[2] != cnn.input_channels:
            logger.info("Dimensions mismatch")
            raise PermissionDenied

        try:
            before = time.time()
            class_probabilities = cnn.inference(face_img[None, :])[0]
            after = time.time()
            # TODO remove time measurement
            logger.debug("Inference took {} seconds ...".format(after - before))
            most_likely_class = np.argmax(class_probabilities)
            if class_probabilities[most_likely_class] <= 0.5 or user.id != most_likely_class:
                raise PermissionDenied
            return user
        except Exception as e:
            logger.error("Exception in face recognition: {} ({})".format(str(e), type(e)))

    def get_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return None
