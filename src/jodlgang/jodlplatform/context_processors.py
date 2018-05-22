""" custom context processors """
from django.conf import settings
from .models import User


def show_ambassador(request):
    team_id = getattr(settings, "TEAM_ID", None)
    ambassador_user = User.objects.get(id=team_id)
    if not ambassador_user:
        return {}

    return {"ambassador_name": ambassador_user.name, "ambassador_email": ambassador_user.email}
