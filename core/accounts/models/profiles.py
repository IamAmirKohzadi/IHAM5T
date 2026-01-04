from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .users import User


# Stores extra user-facing profile data.
class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250,blank=True)
    last_name = models.CharField(max_length=250,blank=True)
    image = models.ImageField(blank=True,null=True)
    description = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    behance_url = models.URLField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Display the owning user's email in admin lists.
        return self.user.email
    
@receiver(post_save,sender=User)
def save_profile(sender,instance,created,**kwargs):
    # Create a profile automatically when a new user is created.
    if created:
        Profile.objects.create(user=instance)
