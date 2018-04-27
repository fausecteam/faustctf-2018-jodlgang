from django.conf import settings
from .models import User


class FaceAuthenticationBackend:
    def authenticate(self, request, token=None):
        # Check the token and return the user
        return None

    def get_user(self, user_id):
        return None