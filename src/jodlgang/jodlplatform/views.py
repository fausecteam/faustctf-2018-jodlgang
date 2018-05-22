from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from .models import User, Note


def index(request):
    team_id = getattr(settings, "TEAM_ID", None)
    user = User.objects.get(id=team_id)
    # TODO what if user does not exist?

    context = {
        "name": user.name,
        "email": user.email
    }
    return render(request, "index.html", context=context)


@login_required(login_url="/login/")
def home(request):
    team_id = getattr(settings, "TEAM_ID", None)
    user = User.objects.get(id=team_id)
    # TODO what if user does not exist?

    # Get the latest notes
    # TODO get all notes of user currently logged in
    latest_notes = Note.objects.filter(public=True).order_by("-pub_date")[:30]

    context = {
        "name": user.name,
        "email": user.email,
        "notes": latest_notes
    }

    return render(request, "home.html", context=context)


@login_required(login_url="/login/")
def add_note(request):
    team_id = getattr(settings, "TEAM_ID", None)
    ambassador_user = User.objects.get(id=team_id)
    # TODO what if user does not exist?

    context = {
        "name": ambassador_user.name,
        "email": ambassador_user.email
    }

    current_user = request.user
    if "note" in request.POST and "title" in request.POST:
        public = "public" in request.POST
        text = request.POST["note"]
        title = request.POST["title"]
        if len(text) > 0 and len(title):
            Note(author=current_user, text=text, title=title, public=public).save()
            return render(request, "added_note.html", context=context)

    return render(request, "add_note.html", context=context)


@login_required(login_url="/login/")
def personal_notes(request):
    team_id = getattr(settings, "TEAM_ID", None)
    user = User.objects.get(id=team_id)
    # TODO what if user does not exist?

    # Get the latest notes
    user_personal_notes = Note.objects.filter(author=request.user).order_by("-pub_date")

    context = {
        "name": user.name,
        "email": user.email,
        "notes": user_personal_notes
    }

    return render(request, "home.html", context=context)
