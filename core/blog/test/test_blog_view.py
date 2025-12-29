from django.test import TestCase,Client
from django.urls import reverse
from accounts.models import User,Profile
from blog.models import Post,Category
from datetime import datetime
class TestBlogViews(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@test.com',password='Mam54321')
        self.profile = Profile.objects.create(
            user = self.user,
            first_name = 'test_first_name',
            last_name = 'test_last_name',
            description = 'test_description',
            )
        self.post = Post.objects.create(
            author = self.profile,
            title = 'test',
            content ='test1',
            category = None,
            status = True,
            published_date = datetime.now()
        )

    def test_blog_index_url_response(self):
        url = reverse('blog:cbv-index')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(template_name = 'index.html')

    def test_blog_post_details_logged_in_response(self):
        self.client.force_login(self.user)
        url = reverse('blog:post-detail',kwargs={'pk':self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)

    def test_blog_post_details_anonymous_response(self):
        url = reverse('blog:post-detail',kwargs={'pk':self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,302)#302 is redirected code!we get redirected to login page!