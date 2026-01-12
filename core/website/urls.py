# website/urls.py
from django.urls import path
from .views import *

app_name = "website"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path('about/',AboutView.as_view(),name='about'),
    path('contact/',ContactView.as_view(),name='contact'),
    path('story-tip/',StoryTipView.as_view(),name='story-tip'),
    path('newsletter/',NewsletterView.as_view(),name='newsletter'),
    path('blog/',BlogHome.as_view(),name='blog-home'),
    path('blog/<int:pk>/',BlogSingle.as_view(),name='blog-single'),

]
