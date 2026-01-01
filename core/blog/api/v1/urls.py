from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views


app_name = 'api-v1'
#dynamic url pattern using DefaultRouter!it uses the PostModelViewSet and CategoryModelViewSet and generate urls for them base on their function automatically!#
router = DefaultRouter()

router.register('post',views.PostModelViewSet,basename='post') #post-list
router.register('category',views.CategoryModelViewSet,basename='category') #category-list
router.register('comment',views.CommentModelViewSet,basename='comment') #comment-list
router.register('comment-report',views.CommentReportViewSet,basename='comment-report') #comment-report-list
router.register('post-report',views.PostReportViewSet,basename='post-report') #post-report-list

urlpatterns = router.urls



#static url pattern assignment,which is tedious!#
# urlpatterns = [
#     path('post/',views.postList,name='post-list'),  
#     path('post/<int:pk>/',views.PostViewSet.as_view({'get':'retrieve'}),name='post-detail'), 
#     path('post/',views.PostViewSet.as_view({'get':'list'}),name='post-list'),
#     path('post/<int:pk>/',views.PostDetail.as_view(),name='post-detail'),
# ]
