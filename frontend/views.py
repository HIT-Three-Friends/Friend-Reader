from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def show_activities(request):
    return render(request, "show_activities.html")


def show_vitalities(request):
    return render(request, "show_vitalities.html")


def show_interests(request):
    return render(request, "show_interests.html")


def config_user(request):
    return render(request, "config_user.html")


def config_friends(request):
    return render(request, "config_friends.html")


def show_changes(request):
    return render(request, "show_changes.html")


def show_interactions(request):
    return render(request, "show_interactions.html")

