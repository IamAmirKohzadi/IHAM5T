from django.test import TestCase
from django.urls import reverse


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
