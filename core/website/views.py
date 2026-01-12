from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import FormView, TemplateView

from accounts.models import Profile
from core.recaptcha import verify_recaptcha
from .forms import ContactMessageForm, StoryTipForm, NewsletterSubscriberForm

# Renders the website home page.
class HomeView(TemplateView):
    template_name = "website/index.html"

# Renders the about page.
class AboutView(TemplateView):
    template_name = "website/about.html"

# Renders and handles the contact form.
class ContactView(FormView):
    template_name = "website/contact.html"
    form_class = ContactMessageForm
    success_url = reverse_lazy("website:contact")

    def get_form_kwargs(self):
        # Attach the request user so the form can relax required fields.
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Verify reCAPTCHA for guests, then persist with auto-filled sender info.
        message = form.save(commit=False)
        user = self.request.user
        if not user or not user.is_authenticated:
            token = self.request.POST.get("g-recaptcha-response")
            is_valid, error_message = verify_recaptcha(token, self.request.META.get("REMOTE_ADDR"))
            if not is_valid:
                form.add_error(None, error_message)
                return self.form_invalid(form)
        if user and user.is_authenticated:
            profile = Profile.objects.filter(user=user).first()
            full_name = ""
            if profile:
                full_name = f"{profile.first_name} {profile.last_name}".strip()
            message.name = full_name or user.email
            message.email = user.email
        message.save()
        messages.success(self.request, "Your message has been received.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Surface validation errors in the UI.
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

# Renders and handles story tip submissions.
class StoryTipView(FormView):
    form_class = StoryTipForm
    success_url = reverse_lazy("website:story-tip")

    def get(self, request, *args, **kwargs):
        # Redirect direct visits since the form is shown in a modal.
        return redirect("website:index")

    def get_form_kwargs(self):
        # Attach the request user so the form can relax required fields.
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Verify reCAPTCHA for guests, then persist with auto-filled contact info.
        tip = form.save(commit=False)
        user = self.request.user
        if not user or not user.is_authenticated:
            token = self.request.POST.get("g-recaptcha-response")
            is_valid, error_message = verify_recaptcha(token, self.request.META.get("REMOTE_ADDR"))
            if not is_valid:
                form.add_error(None, error_message)
                if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"detail": error_message}, status=400)
                return self.form_invalid(form)
        if user and user.is_authenticated:
            profile = Profile.objects.filter(user=user).first()
            full_name = ""
            if profile:
                full_name = f"{profile.first_name} {profile.last_name}".strip()
            tip.contact_name = full_name or user.email
            tip.contact_email = user.email
        tip.save()
        messages.success(self.request, "Your story tip has been submitted.")
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"message": "Your story tip has been submitted."}, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Surface validation errors in the UI.
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "errors": form.errors,
                    "non_field_errors": form.non_field_errors(),
                },
                status=400,
            )
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

# Renders and handles the newsletter subscription form.
class NewsletterView(FormView):
    template_name = "blogApi/blog-newsletter.html"
    form_class = NewsletterSubscriberForm
    success_url = reverse_lazy("website:newsletter")

    def form_valid(self, form):
        # Save the subscriber and show a success message.
        form.save()
        messages.success(self.request, "You are subscribed to the newsletter.", extra_tags="newsletter")
        return redirect(self.request.META.get("HTTP_REFERER", self.get_success_url()))

    def form_invalid(self, form):
        # Surface subscription errors via messages.
        error_message = form.errors.get("email", ["Unable to subscribe."])[0]
        messages.error(self.request, error_message, extra_tags="newsletter")
        return redirect(self.request.META.get("HTTP_REFERER", self.get_success_url()))

# Renders the blog home page shell.
class BlogHome(TemplateView):
    template_name = "blogApi/blog-home.html"

# Renders the blog single-post page shell.
class BlogSingle(TemplateView):
    template_name = "blogApi/blog-single.html"
