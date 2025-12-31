from django.test import TestCase
from ..models import Post,Category
from datetime import datetime
from accounts.models import User,Profile

class TestPostModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@test.com',password='Mam54321')
        self.profile = Profile.objects.create(
            user = self.user,
            first_name = 'test_first_name',
            last_name = 'test_last_name',
            description = 'test_description',
            )
    def test_create_post(self):
        category = Category.objects.create(name='test')
        post = Post.objects.create(
            author = self.profile,
            title = 'test',
            content ='test1',
            status = True,
            published_date = datetime.now()
        )
        post.categories.add(category)
        self.assertTrue(Post.objects.filter(pk=post.id).exists())
    
    
