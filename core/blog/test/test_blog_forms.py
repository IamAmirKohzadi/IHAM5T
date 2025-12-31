from django.test import TestCase
#TestCase will test everything in a dummy DB,then deletes it!
from ..forms import PostFrom
from ..models import Category
from datetime import datetime


class test_post_form(TestCase):
    def test_post_form_with_valid_data(self):
        cat_obj = Category.objects.create(name='apple')
        form = PostFrom(data={
            'title':'test',
            'content':'test1',
            'categories':[cat_obj.id],
            'status':True,
            'published_date':datetime.now(),
        })
        self.assertTrue(form.is_valid())
