from django.shortcuts import (render,
                              redirect,)
from django.views.generic import (ListView,
                                  DetailView,
                                  FormView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,)
from django.views.generic.base import (TemplateView,
                                       RedirectView,)
from accounts.models import Profile
from .models import Post
from .forms import PostFrom
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


'''
class based views all this page!
'''
class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'AMIR'
        return context

class RedirectToGoogle(RedirectView):
    url = 'https://google.com'

class PostList(LoginRequiredMixin,ListView):
    context_object_name = 'posts'
    def  get_queryset(self):
        posts = Post.objects.all()
        return posts
    
class PostListApi(TemplateView):
    template_name = 'blog/post_list_api.html'
    

class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    form_class = PostFrom
    success_url = '/blog/post/'

    def form_valid(self, form):
        form.instance.author = Profile.objects.get(user=self.request.user)
        return super().form_valid(form)
    
class PostEditView(LoginRequiredMixin,UpdateView):
    model = Post
    form_class = PostFrom
    success_url = '/blog/post/'
    #we are creating this filter in order that only the user owner or admin can edit a post!#
    def get_queryset(self):
        return Post.objects.filter(author__user=self.request.user)

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = '/blog/post/'
    #we are creating this filter in order that only the user owner or admin can delete a post!#
    def get_queryset(self):
        return Post.objects.filter(author__user=self.request.user)
