from django.test import TestCase
from django.urls import reverse


class TestWebsiteUrls(TestCase):
    def test_home_url(self):
        self.assertEqual(reverse("website:index"), "/")

    def test_about_url(self):
        self.assertEqual(reverse("website:about"), "/about/")

    def test_contact_url(self):
        self.assertEqual(reverse("website:contact"), "/contact/")

    def test_newsletter_url(self):
        self.assertEqual(reverse("website:newsletter"), "/newsletter/")

    def test_blog_home_url(self):
        self.assertEqual(reverse("website:blog-home"), "/blog/")

    def test_blog_single_url(self):
        self.assertEqual(reverse("website:blog-single", kwargs={"pk": 1}), "/blog/1/")
