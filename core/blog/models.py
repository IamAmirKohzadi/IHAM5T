from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

class Post(models.Model):
    '''
    this is a class for define posts for blog app
    '''
    author = models.ForeignKey('accounts.Profile',on_delete=models.CASCADE)
    counted_view = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True,blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.BooleanField()
    categories = models.ManyToManyField("Category", blank=True, related_name="posts")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=255,unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(Lower('name'), name='category_name_ci_unique'),
        ]

    def __str__(self):
        return self.name
