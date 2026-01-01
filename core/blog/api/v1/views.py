from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView,ListCreateAPIView
from rest_framework import mixins,viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count,F,Sum
from django.utils import timezone
from .serializers import PostSerializer,CategorySerializer,CommentSerializer,CommentReportSerializer,PostReportSerializer
from .permissions import IsOwnerOrReadOnly, IsCommentOwnerOrReadOnly, IsVerifiedOrReadOnly
from .paginations import LargeResultsSetPagination
from blog.models import Post,Category,Comment,CommentReport,PostReport,PostReaction
from django.db.models import Q
from accounts.models import Profile

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
    permission_classes = [IsAuthenticatedOrReadOnly, IsVerifiedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = {
        'categories': ['exact'],
        'author': ['exact'],
        'status': ['exact'],
        'published_date': ['date', 'gte', 'lte'],
        'counted_view': ['gte', 'lte'],
    }
    search_fields = ['title','content']
    ordering_fields = ['published_date', 'counted_view', 'created_date']

    def get_queryset(self):
        qs = Post.objects.all().annotate(
            likes_count=Count('reactions', filter=Q(reactions__value=1), distinct=True),
            dislikes_count=Count('reactions', filter=Q(reactions__value=-1), distinct=True),
            comments_count=Count('comments', filter=Q(comments__is_approved=True), distinct=True),
        )
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return qs.filter(status=True)

        if user.is_staff:
            return qs

        if getattr(self, "action", None) in ("destroy", "update", "partial_update"):
            return qs.filter(Q(status=True) | Q(author__user=user))

        author_param = self.request.query_params.get("author")
        include_unapproved = self.request.query_params.get("include_unapproved")
        if author_param and include_unapproved in ("1", "true", "True"):
            try:
                author_id = int(author_param)
            except (TypeError, ValueError):
                author_id = None
            if author_id:
                profile_id = Profile.objects.filter(user=user).values_list("id", flat=True).first()
                if profile_id and profile_id == author_id:
                    return qs

        return qs.filter(status=True)

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)
        if not user or not user.is_staff:
            serializer.save(status=False)
            return
        serializer.save(status=True)

    def perform_update(self, serializer):
        user = getattr(self.request, "user", None)
        if not user or not user.is_staff:
            serializer.save(status=serializer.instance.status)
            return
        serializer.save()

    def retrieve(self, request, *args, **kwargs):#we use session based so user does not increase the views by refreshing!
        instance = self.get_object()
        session_key = f"viewed_post_{instance.pk}"

        if not request.session.get(session_key):
            Post.objects.filter(pk=instance.pk).update(counted_view=F("counted_view") + 1)
            request.session[session_key] = True
            request.session.modified = True

        instance.refresh_from_db(fields=["counted_view"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsVerifiedOrReadOnly])
    def react(self, request, *args, **kwargs):
        post = self.get_object()
        try:
            value = int(request.data.get("value"))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid reaction value."}, status=400)
        if value not in (1, -1):
            return Response({"detail": "Invalid reaction value."}, status=400)

        profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"detail": "Profile not found."}, status=400)

        reaction, created = PostReaction.objects.get_or_create(
            post=post, user=profile, defaults={"value": value}
        )
        if not created:
            if reaction.value == value:
                reaction.delete()
                current = 0
            else:
                reaction.value = value
                reaction.save(update_fields=["value", "updated_date"])
                current = value
        else:
            current = value

        counts = PostReaction.objects.filter(post=post).aggregate(
            likes=Count('id', filter=Q(value=1)),
            dislikes=Count('id', filter=Q(value=-1)),
        )

        return Response({
            "likes_count": counts.get("likes", 0),
            "dislikes_count": counts.get("dislikes", 0),
            "user_reaction": current,
        })

    @action(detail=False, methods=['get'])#we use this def to choose the blogger of the month based on total views in the last 30 days, with a minimum post count (e.g., at least 2 posts) to avoid one‑hit wins!
    def top_author(self, request):
        try:
            days = int(request.query_params.get('days', 30))
        except (TypeError, ValueError):
            days = 30
        try:
            min_posts = int(request.query_params.get('min_posts', 2))
        except (TypeError, ValueError):
            min_posts = 2

        since = timezone.now() - timezone.timedelta(days=days)
        stats = (Post.objects.filter(published_date__gte=since)
                 .values('author_id')
                 .annotate(total_views=Sum('counted_view'), post_count=Count('id'))
                 .filter(post_count__gte=min_posts)
                 .order_by('-total_views')
                 .first())

        if not stats:
            stats = (Post.objects.values('author_id')
                     .annotate(total_views=Sum('counted_view'), post_count=Count('id'))
                     .order_by('-total_views')
                     .first())

        if not stats:
            return Response({})

        author = Profile.objects.select_related('user').filter(pk=stats['author_id']).first()
        if not author:
            return Response({})

        author_name = f"{author.first_name} {author.last_name}".strip()
        if not author_name:
            author_name = author.user.email

        author_image = None
        if author.image:
            author_image = request.build_absolute_uri(author.image.url)

        return Response({
            'author_id': author.id,
            'author_name': author_name,
            'author_email': author.user.email,
            'author_image': author_image,
            'author_description': author.description,
            'social_links': {
                'facebook': author.facebook_url,
                'twitter': author.twitter_url,
                'github': author.github_url,
                'behance': author.behance_url,
            },
            'total_views': stats.get('total_views') or 0,
            'post_count': stats.get('post_count') or 0,
            'period_days': days,
        })

class CategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CommentModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsVerifiedOrReadOnly, IsCommentOwnerOrReadOnly]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["post", "parent", "author"]
    ordering_fields = ["created_date"]
    ordering = ["created_date"]


class CommentReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentReportSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "comment", "reporter"]

    def get_queryset(self):
        qs = CommentReport.objects.all()
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return CommentReport.objects.none()
        if user.is_staff:
            return qs
        return qs.filter(Q(comment__post__author__user=user) | Q(comment__author__user=user))


class PostReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PostReportSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "post", "reporter"]

    def get_queryset(self):
        qs = PostReport.objects.all()
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return PostReport.objects.none()
        if user.is_staff:
            return qs
        return qs.filter(post__author__user=user)




    
