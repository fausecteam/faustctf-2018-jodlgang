from django.conf import settings
from .models import User


class FaceAuthenticationBackend(object):
    def authenticate(self, request, **kwargs):
        # Check the token and return the user
        try:
            user = User.objects.get(email=kwargs["username"])
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
