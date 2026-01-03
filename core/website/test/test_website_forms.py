from django.forms import modelform_factory
from django.test import TestCase

from website.models import SiteSettings


class TestWebsiteForms(TestCase):
    def test_site_settings_form_allows_blank_quote(self):
        SettingsForm = modelform_factory(SiteSettings, fields=["blog_quote"])
        form = SettingsForm(data={"blog_quote": ""})
        self.assertTrue(form.is_valid())
