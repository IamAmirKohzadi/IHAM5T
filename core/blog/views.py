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
# Home page view for the blog app.
class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        # Inject extra context for the template.
        context = super().get_context_data(**kwargs)
        context['name'] = 'AMIR'
        return context

# Simple redirect view to an external URL.
class RedirectToGoogle(RedirectView):
    url = 'https://google.com'

# Lists all posts for authenticated users.
class PostList(LoginRequiredMixin,ListView):
    context_object_name = 'posts'
    def  get_queryset(self):
        # Return all posts for the list view.
        posts = Post.objects.all()
        return posts
    
# Static page that documents or consumes the post list API.
class PostListApi(TemplateView):
    template_name = 'blog/post_list_api.html'
    

# Shows a single post in the template view.
class PostDetailView(LoginRequiredMixin,DetailView):
    model = Post


# Creates a post and assigns the current user as author.
class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    form_class = PostFrom
    success_url = '/blog/post/'

    def form_valid(self, form):
        # Attach the logged-in user's profile as the post author.
        form.instance.author = Profile.objects.get(user=self.request.user)
        return super().form_valid(form)
    
# Updates a post with owner/admin filtering.
class PostEditView(LoginRequiredMixin,UpdateView):
    model = Post
    form_class = PostFrom
    success_url = '/blog/post/'
    #we are creating this filter in order that only the user owner or admin can edit a post!#
    def get_queryset(self):
        # Limit edit access to owners or admins.
        if self.request.user.is_superuser:
            return Post.objects.all()
        return Post.objects.filter(author__user=self.request.user)

# Deletes a post with owner/admin filtering.
class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = '/blog/post/'
    #we are creating this filter in order that only the user owner or admin can delete a post!#
    def get_queryset(self):
        # Limit delete access to owners or admins.
        if self.request.user.is_superuser:
            return Post.objects.all()
        return Post.objects.filter(author__user=self.request.user)
