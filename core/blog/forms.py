from django import forms
from .models import Post
class PostFrom(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title','content','extra_content','image','image_2','image_3','status','categories','published_date']
