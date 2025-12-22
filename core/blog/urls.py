from django.urls import path,include
from . import views
# from .views import indexView
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

app_name = 'blog'

urlpatterns = [
    # path('', TemplateView.as_view(template_name='index.html')),
    path('',views.IndexView.as_view(),name='cbv-index'),
    path('post/',views.PostList.as_view(),name='post-list'),
    path('post/api',views.PostListApi.as_view(),name='post-list-api'),
    path('post/<int:pk>',views.PostDetailView.as_view(),name='post-detail'),
    path('post/<int:pk>/edit',views.PostEditView.as_view(),name='post-edit'),
    path('post/<int:pk>/delete',views.PostDeleteView.as_view(),name='post-delete'),
    path('post/create',views.PostCreateView.as_view(),name='post-create'),
    path('gomaktab',views.RedirectToMaktab.as_view(),name='redirect-maktab'),
    path('api/v1/', include('blog.api.v1.urls'))
]
