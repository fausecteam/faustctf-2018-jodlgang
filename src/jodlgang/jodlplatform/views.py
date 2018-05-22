from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Note


def index(request):
    return render(request, "index.html")


@login_required(login_url="/login/")
def home(request):
    # Get the latest notes
    latest_notes = Note.objects.filter(public=True).order_by("-pub_date")[:30]

    context = {
        "notes": latest_notes
    }

    return render(request, "home.html", context=context)


@login_required(login_url="/login/")
def add_note(request):
    current_user = request.user
    if "note" in request.POST and "title" in request.POST:
        public = "public" in request.POST
        text = request.POST["note"]
        title = request.POST["title"]
        if len(text) > 0 and len(title):
            Note(author=current_user, text=text, title=title, public=public).save()
            return render(request, "added_note.html")

    # On error show the form again
    return render(request, "add_note.html")


@login_required(login_url="/login/")
def personal_notes(request):
    # Get all personal notes
    user_personal_notes = Note.objects.filter(author=request.user).order_by("-pub_date")

    context = {
        "notes": user_personal_notes
    }

    return render(request, "home.html", context=context)
