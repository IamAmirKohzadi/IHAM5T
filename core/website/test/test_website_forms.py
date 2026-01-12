from django.forms import modelform_factory
from django.test import TestCase

from accounts.models import User
from website.forms import NewsletterSubscriberForm, StoryTipForm
from website.models import SiteSettings, NewsletterSubscriber


class TestWebsiteForms(TestCase):
    def test_site_settings_form_allows_blank_quote(self):
        SettingsForm = modelform_factory(SiteSettings, fields=["blog_quote"])
        form = SettingsForm(data={"blog_quote": ""})
        self.assertTrue(form.is_valid())

    def test_newsletter_form_rejects_duplicate_email(self):
        NewsletterSubscriber.objects.create(email="news@test.com")
        form = NewsletterSubscriberForm(data={"email": "news@test.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_story_tip_form_relaxes_contact_fields_for_user(self):
        user = User.objects.create_user(email="user@test.com", password="TestPass123!")
        form = StoryTipForm(
            data={
                "title": "Tip title",
                "summary": "Summary",
                "details": "Full details",
            },
            user=user,
        )
        self.assertTrue(form.is_valid())
