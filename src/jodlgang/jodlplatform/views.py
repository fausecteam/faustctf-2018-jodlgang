from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from .models import User


def index(request):
    team_id = getattr(settings, "TEAM_ID", None)
    user = User.objects.get(id=team_id)
    # TODO what if user does not exist?

    context = {
        "name": user.name,
        "email": user.email
    }
    return render(request, "home.html", context=context)


def my_view(request):
    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        # Redirect to success page
        return render(request, "registration/logged_out.html")
    else:
        # Return to invalid login error message
        return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return render(request, "registration/logged_out.html")
