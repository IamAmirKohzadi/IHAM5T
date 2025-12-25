from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView,ListCreateAPIView
from rest_framework import mixins,viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .serializers import PostSerializer,CategorySerializer
from .permissions import IsOwnerOrReadOnly
from .paginations import LargeResultsSetPagination
from blog.models import Post,Category

#function based api for listing all the posts with permission classes and decorators!#
# @api_view(['GET','POST'])
# @permission_classes([IsAuthenticatedOrReadOnly])
# def postList(request):
#     if request.method == 'GET':
#         posts = Post.objects.all()
#         serializer = PostSerializer(posts,many=True)#many=True so postserializer understand that number of post can be more than 1!#
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = PostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)
        

#class based api for listing all the posts with permission classes!it handles the http methods such as GET,POST,etc so we dont need @api_view decorator!#
#it handles get and post as a pre-defined function!#
# class PostList(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = PostSerializer
#     def get(self,request):
#         posts = Post.objects.all()
#         serializer = PostSerializer(posts,many=True)
#         return Response(serializer.data)
#     def post(self,request):
#         serializer = PostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)

#same as APIview but its Much less code,Cleaner and easier to extend!#     
# class PostList(ListCreateAPIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = PostSerializer
#     queryset = Post.objects.all()
#     def post(self,request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)
    

#function based api for post details with permission classes and decorators!#
# @api_view(['GET','PUT','DELETE'])
# @permission_classes([IsAuthenticated])
# def postDetail(request,id):
#     post = get_object_or_404(Post,pk=id)
#     if request.method == 'GET':
#         serializer = PostSerializer(post)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = PostSerializer(post,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         post.delete()
#         return Response('deleted!')


#class based api for detail of the posts with permission classes!it handles the http methods such as GET,PUT,etc so we dont need @api_view decorator!#
# class PostDetail(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = PostSerializer
#     def get_object(self,id):
#         return get_object_or_404(Post,pk=id)
#     def get(self,request,id):
#         post = self.get_object(id)
#         serializer = self.serializer_class(post)
#         return Response(serializer.data)
#editing the post data!#
#     def put(self,request,id):
#         post = self.get_object(id)
#         serializer = PostSerializer(post,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     def delete(self,request,id):
#         post = self.get_object(id)
#         post.delete()
#         return Response('deleted!')
    
#generic class that simplifies building single-item API endpoints for Retrieve, Update, and Destroy (CRUD) operations, handling GET, PUT/PATCH, and DELETE requests for a specific model instance without writing repetitive code!# 
# It combines RetrieveModelMixin, UpdateModelMixin, and DestroyModelMixin!#   
# class PostDetail(RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = PostSerializer
#     queryset = Post.objects.all()

        

#a class-based view that provides a set of default actions for performing CRUD operations on a model!#
class PostModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = LargeResultsSetPagination
    queryset = Post.objects.all()
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['category','author','status']
    search_fields = ['title','content']
    ordering_fields = ['published_date']

class CategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()




    
