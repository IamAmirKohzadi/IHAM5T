from django.shortcuts import render
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "website/index.html"

class AboutView(TemplateView):
    template_name = "website/about.html"

class ContactView(TemplateView):
    template_name = "website/contact.html"

class NewsletterView(TemplateView):
    template_name = "website/newsletter.html"
