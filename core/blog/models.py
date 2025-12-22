from django.db import models

class Post(models.Model):
    '''
    this is a class for define posts for blog app
    '''
    author = models.ForeignKey('accounts.Profile',on_delete=models.CASCADE)
    image = models.ImageField(null=True,blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.BooleanField()
    category = models.ForeignKey("Category",on_delete=models.SET_NULL,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name


