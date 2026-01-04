from rest_framework import serializers
from django.db.models import Q
from django.db.models.functions import Coalesce
from blog.models import Post,Category,Comment,CommentReport,PostReport,PostReaction
from friends.models import Friendship
from django.urls import reverse
from accounts.models import Profile
from django.utils.text import Truncator
#convert data into jason so we can screen it!#


# class PostSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     author = serializers.CharField(max_length=255)

# we use serializer when we need more control, customization, or are working with non-model data!#
# but we use ModelSerializer when we are dealing with models in a standard CRUD context!#
# Serializes categories with case-insensitive name validation.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name','id']

    def validate_name(self, value):
        # Normalize the name and enforce case-insensitive uniqueness.
        name = value.strip()
        qs = Category.objects.filter(name__iexact=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return name

# Serializes posts with related metadata and user-specific fields.
class PostSerializer(serializers.ModelSerializer):
    urls = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_id = serializers.IntegerField(read_only=True)
    author_social_links = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    user_reaction = serializers.SerializerMethodField()
    previous_post = serializers.SerializerMethodField()
    next_post = serializers.SerializerMethodField()
    categories = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Category.objects.all())
    categories_info = CategorySerializer(source='categories', many=True, read_only=True)
    excerpt = serializers.SerializerMethodField()
    status = serializers.BooleanField(required=False)
    class Meta:
        model = Post
        fields = ['id','author_id','author_name','author_social_links','can_edit','likes_count','dislikes_count','comments_count','user_reaction','image','image_2','image_3','title','excerpt','content','extra_content','categories','categories_info','status','urls','created_date','published_date','counted_view','previous_post','next_post']
        read_only_fields = ['author_name','can_edit']

    def get_urls(self,obj):
        # Build relative and absolute URLs for the post.
        request = self.context.get('request')
        relative_url = reverse('blog:api-v1:post-detail', args=[obj.pk])
        absolute_url = request.build_absolute_uri(relative_url) if request else None
        return {
            "relative": relative_url,
            "absolute": absolute_url,
        }
    
    def get_author_name(self,obj):
        # Format the author's first and last name.
        return f'{obj.author.first_name} {obj.author.last_name}'

    def get_author_social_links(self, obj):
        # Expose the author's social links for the client UI.
        return {
            'facebook': obj.author.facebook_url,
            'twitter': obj.author.twitter_url,
            'github': obj.author.github_url,
            'behance': obj.author.behance_url,
        }

    def get_user_reaction(self, obj):
        # Return the current user's reaction value for this post.
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        profile = Profile.objects.filter(user_id=request.user.id).first()
        if not profile:
            return 0
        reaction = PostReaction.objects.filter(post=obj, user=profile).first()
        return reaction.value if reaction else 0

    def get_can_edit(self, obj):
        # Allow edits for staff or the post author.
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return obj.author and obj.author.user_id == request.user.id

    def get_previous_post(self, obj):
        # Locate the previous post by publish/created date ordering.
        sort_date = obj.published_date or obj.created_date
        queryset = Post.objects.annotate(sort_date=Coalesce('published_date', 'created_date'))
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_staff:
            queryset = queryset.filter(status=True)
        prev_post = (queryset
                     .filter(Q(sort_date__lt=sort_date) | Q(sort_date=sort_date, pk__lt=obj.pk))
                     .order_by('-sort_date', '-pk')
                     .first())
        if not prev_post:
            return None
        return {'id': prev_post.id, 'title': prev_post.title}

    def get_next_post(self, obj):
        # Locate the next post by publish/created date ordering.
        sort_date = obj.published_date or obj.created_date
        queryset = Post.objects.annotate(sort_date=Coalesce('published_date', 'created_date'))
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_staff:
            queryset = queryset.filter(status=True)
        next_post = (queryset
                     .filter(Q(sort_date__gt=sort_date) | Q(sort_date=sort_date, pk__gt=obj.pk))
                     .order_by('sort_date', 'pk')
                     .first())
        if not next_post:
            return None
        return {'id': next_post.id, 'title': next_post.title}

    def get_excerpt(self, obj):
        # Create a 30-word excerpt for list views.
        return Truncator(obj.content).words(30, truncate="...")
    
    #to_representation is used to only and only for showing the data differently!(not editing!)#
    def to_representation(self, instance):
        # Shape list vs detail responses by removing fields.
        request = self.context.get('request')
        rep = super().to_representation(instance)
        if request.parser_context.get('kwargs').get('pk'):#this means that request is asking for post details,not post list!#
            rep.pop('urls')#for showing the detail part of api!#
        else:
            rep.pop('content')#for showing the list part of api!#
            rep.pop('extra_content', None)
            rep.pop('previous_post', None)
            rep.pop('next_post', None)
        return rep
    
    def create(self, validated_data):#check that for creating the post,user is assigned automatically! #
        # Attach the current user's profile as the author.
        validated_data['author'] = Profile.objects.get(user__id = self.context.get('request').user.id)
        return super().create(validated_data)


# Serializes comments and enforces depth/rules.
class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    author_id = serializers.IntegerField(read_only=True)
    author_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "parent",
            "depth",
            "author_id",
            "author_name",
            "is_owner",
            "name",
            "message",
            "created_date",
        ]
        read_only_fields = ["depth", "author_id", "author_name", "is_owner", "created_date"]

    def get_author_name(self, obj):
        # Return the author's display name or anonymous name.
        if obj.author:
            full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
            return full_name or obj.author.user.email
        return obj.name

    def get_is_owner(self, obj):
        # Check if the current user owns the comment.
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if not obj.author:
            return False
        return obj.author.user_id == request.user.id

    def validate(self, attrs):
        # Validate parent depth, post approval, and friend-only rules.
        parent = attrs.get("parent")
        post = attrs.get("post")
        if parent:
            if post and parent.post_id != post.id:
                raise serializers.ValidationError("Parent comment must belong to the same post.")
            if parent.depth >= 2:
                raise serializers.ValidationError("Max comment depth reached.")
        if not self.instance and post and not post.status:
            request = self.context.get("request")
            if not request or not request.user or not request.user.is_staff:
                raise serializers.ValidationError("Comments are disabled until the post is approved.")
        if not self.instance and post:
            request = self.context.get("request")
            if request and request.user and request.user.is_authenticated and not request.user.is_staff:
                post_author = post.author
                if post_author and post_author.user_id != request.user.id:
                    profile = Profile.objects.filter(user_id=request.user.id).first()
                    if profile and not Friendship.objects.filter(
                        Q(user_a=profile, user_b=post_author) | Q(user_a=post_author, user_b=profile)
                    ).exists():
                        raise serializers.ValidationError("Only friends can comment on this post.")
        return attrs

    def validate_message(self, value):
        # Prevent empty comment messages.
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value

    def create(self, validated_data):
        # Set depth and attach author or require a name.
        request = self.context.get("request")
        parent = validated_data.get("parent")
        validated_data["depth"] = parent.depth + 1 if parent else 0
        if request and request.user and request.user.is_authenticated:
            validated_data["author"] = Profile.objects.get(user__id=request.user.id)
        elif not validated_data.get("name"):
            raise serializers.ValidationError({"name": "Name is required for anonymous comments."})
        return super().create(validated_data)


# Serializes comment reports with related post/comment data.
class CommentReportSerializer(serializers.ModelSerializer):
    reporter_id = serializers.IntegerField(read_only=True)
    reporter_name = serializers.SerializerMethodField()
    comment_message = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = CommentReport
        fields = [
            "id",
            "comment",
            "comment_message",
            "post_id",
            "post_title",
            "reason",
            "status",
            "reporter_id",
            "reporter_name",
            "created_date",
        ]
        read_only_fields = ["status", "reporter_id", "reporter_name", "created_date"]

    def get_reporter_name(self, obj):
        # Provide reporter display name or anonymous label.
        if obj.reporter:
            full_name = f"{obj.reporter.first_name} {obj.reporter.last_name}".strip()
            return full_name or obj.reporter.user.email
        return "anonymous"

    def get_comment_message(self, obj):
        # Truncate the reported comment for previews.
        if not obj.comment:
            return ""
        return Truncator(obj.comment.message).chars(120, truncate="...")

    def get_post_id(self, obj):
        # Expose the related post ID for admin UI.
        if not obj.comment or not obj.comment.post:
            return None
        return obj.comment.post_id

    def get_post_title(self, obj):
        # Expose the related post title for admin UI.
        if not obj.comment or not obj.comment.post:
            return ""
        return obj.comment.post.title

    def create(self, validated_data):
        # Attach reporter and prevent self/duplicate reports.
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["reporter"] = Profile.objects.get(user__id=request.user.id)
            if validated_data["comment"].author and validated_data["comment"].author.user_id == request.user.id:
                raise serializers.ValidationError({"detail": "You cannot report your own comment."})
            if CommentReport.objects.filter(comment=validated_data["comment"], reporter=validated_data["reporter"]).exists():
                raise serializers.ValidationError({"detail": "You have already reported this comment."})
        return super().create(validated_data)


# Serializes post reports with reporter metadata.
class PostReportSerializer(serializers.ModelSerializer):
    reporter_id = serializers.IntegerField(read_only=True)
    reporter_name = serializers.SerializerMethodField()
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = PostReport
        fields = [
            "id",
            "post",
            "post_title",
            "reason",
            "status",
            "reporter_id",
            "reporter_name",
            "created_date",
        ]
        read_only_fields = ["status", "reporter_id", "reporter_name", "created_date"]

    def get_reporter_name(self, obj):
        # Provide reporter display name or anonymous label.
        if obj.reporter:
            full_name = f"{obj.reporter.first_name} {obj.reporter.last_name}".strip()
            return full_name or obj.reporter.user.email
        return "anonymous"

    def get_post_title(self, obj):
        # Expose the reported post title for admin UI.
        if not obj.post:
            return ""
        return obj.post.title

    def create(self, validated_data):
        # Attach reporter and prevent self/duplicate reports.
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["reporter"] = Profile.objects.get(user__id=request.user.id)
            if validated_data["post"].author and validated_data["post"].author.user_id == request.user.id:
                raise serializers.ValidationError({"detail": "You cannot report your own post."})
            if PostReport.objects.filter(post=validated_data["post"], reporter=validated_data["reporter"]).exists():
                raise serializers.ValidationError({"detail": "You have already reported this post."})
        return super().create(validated_data)
