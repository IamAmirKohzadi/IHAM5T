# website/urls.py
from django.urls import path
from .views import *

app_name = "website"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path('about/',AboutView.as_view(),name='about'),
    path('contact/',ContactView.as_view(),name='contact'),
    path('newsletter',NewsletterView.as_view(),name='newsletter'),
]
