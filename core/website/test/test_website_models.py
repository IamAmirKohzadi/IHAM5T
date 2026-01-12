from django.test import TestCase

from website.models import SiteSettings, StoryTip, NewsletterSubscriber


class TestWebsiteModels(TestCase):
    def test_site_settings_str(self):
        settings = SiteSettings.objects.create(blog_quote="Test quote")
        self.assertEqual(str(settings), "Site Settings")

    def test_site_settings_defaults(self):
        settings = SiteSettings.objects.create()
        self.assertIsNotNone(settings.updated_at)

    def test_story_tip_str(self):
        tip = StoryTip.objects.create(
            title="Tip title",
            summary="Summary",
            details="Details",
            contact_name="Reporter",
            contact_email="reporter@test.com",
        )
        self.assertIn("Tip title", str(tip))

    def test_newsletter_subscriber_str(self):
        subscriber = NewsletterSubscriber.objects.create(email="news@test.com")
        self.assertEqual(str(subscriber), "news@test.com")
