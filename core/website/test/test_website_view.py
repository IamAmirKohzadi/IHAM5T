from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from accounts.models import User
from website.models import StoryTip, NewsletterSubscriber


class TestWebsiteViews(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse("website:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/index.html")

    def test_about_view(self):
        response = self.client.get(reverse("website:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/about.html")

    def test_contact_view(self):
        response = self.client.get(reverse("website:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/contact.html")

    def test_newsletter_view(self):
        response = self.client.get(reverse("website:newsletter"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blogApi/blog-newsletter.html")

    def test_blog_home_view(self):
        response = self.client.get(reverse("website:blog-home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blogApi/blog-home.html")

    def test_blog_single_view(self):
        response = self.client.get(reverse("website:blog-single", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blogApi/blog-single.html")

    def test_story_tip_get_redirects(self):
        response = self.client.get(reverse("website:story-tip"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("website:index"))

    @patch("website.views.verify_recaptcha", return_value=(True, ""))
    def test_story_tip_ajax_submission(self, *_args):
        url = reverse("website:story-tip")
        payload = {
            "contact_name": "Tipster",
            "contact_email": "tip@test.com",
            "title": "New tip",
            "summary": "Short summary",
            "details": "Full details",
        }
        response = self.client.post(
            url,
            payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(StoryTip.objects.filter(title="New tip").exists())

    def test_newsletter_subscription_creates_record(self):
        url = reverse("website:newsletter")
        response = self.client.post(url, {"email": "news@test.com"}, HTTP_REFERER=reverse("website:index"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NewsletterSubscriber.objects.filter(email="news@test.com").exists())
