from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def signup_page(request):
    return render(request, "accounts/signup.html")


@login_required
def profile_page(request):
    return render(request, "accounts/profile.html")
