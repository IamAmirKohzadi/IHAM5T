from django.test import TestCase
from django.urls import reverse


class TestBlogApiUrls(TestCase):
    def test_post_list_url(self):
        self.assertEqual(reverse("blog:api-v1:post-list"), "/blog/api/v1/post/")

    def test_post_detail_url(self):
        self.assertEqual(reverse("blog:api-v1:post-detail", kwargs={"pk": 1}), "/blog/api/v1/post/1/")

    def test_category_list_url(self):
        self.assertEqual(reverse("blog:api-v1:category-list"), "/blog/api/v1/category/")

    def test_comment_list_url(self):
        self.assertEqual(reverse("blog:api-v1:comment-list"), "/blog/api/v1/comment/")
