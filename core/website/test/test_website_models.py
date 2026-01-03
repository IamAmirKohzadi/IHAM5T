from django.test import TestCase

from website.models import SiteSettings


class TestWebsiteModels(TestCase):
    def test_site_settings_str(self):
        settings = SiteSettings.objects.create(blog_quote="Test quote")
        self.assertEqual(str(settings), "Site Settings")

    def test_site_settings_defaults(self):
        settings = SiteSettings.objects.create()
        self.assertIsNotNone(settings.updated_at)
