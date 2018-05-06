from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "home.html")


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
