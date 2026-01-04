from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

class Post(models.Model):
    '''
    this is a class for define posts for blog app
    '''
    author = models.ForeignKey('accounts.Profile',on_delete=models.CASCADE)
    counted_view = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True,blank=True)
    image_2 = models.ImageField(null=True, blank=True)
    image_3 = models.ImageField(null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    extra_content = models.TextField(blank=True)
    status = models.BooleanField()
    categories = models.ManyToManyField("Category", blank=True, related_name="posts")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        # Return the post title for admin displays.
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=255,unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(Lower('name'), name='category_name_ci_unique'),
        ]

    def __str__(self):
        # Return the category name for admin displays.
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    author = models.ForeignKey("accounts.Profile", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    depth = models.PositiveSmallIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show the post id and author/guest label.
        label = self.name or (self.author.user.email if self.author else "anonymous")
        return f"{self.post_id} - {label}"


class CommentReport(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DISMISSED = "dismissed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey("accounts.Profile", on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show the comment id and reporter label.
        label = self.reporter.user.email if self.reporter else "anonymous"
        return f"{self.comment_id} - {label}"


class PostReaction(models.Model):
    VALUE_LIKE = 1
    VALUE_DISLIKE = -1
    VALUE_CHOICES = [
        (VALUE_LIKE, "Like"),
        (VALUE_DISLIKE, "Dislike"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="post_reactions")
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["post", "user"], name="unique_post_reaction"),
        ]

    def __str__(self):
        # Show the post, user, and reaction value.
        return f"{self.post_id} - {self.user_id} ({self.value})"


class PostReport(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DISMISSED = "dismissed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey("accounts.Profile", on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show the post id and reporter label.
        label = self.reporter.user.email if self.reporter else "anonymous"
        return f"{self.post_id} - {label}"
