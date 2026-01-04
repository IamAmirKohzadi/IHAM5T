from django.contrib import admin
from .models import Category, Comment, CommentReport, Post, PostReport, PostReaction
# Register your models here.

# Admin customization for posts including categories display.
class PostAdmin(admin.ModelAdmin):
    list_display = ['author','title','status','counted_view','categories_list','created_date']
    filter_horizontal = ['categories']

    def categories_list(self, obj):
        # Render categories as a comma-separated string in the admin list.
        return ", ".join(obj.categories.values_list("name", flat=True))
    categories_list.short_description = "Categories"

    
admin.site.register(Post,PostAdmin)
admin.site.register(Category)


class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "author", "name", "depth", "is_approved", "created_date"]
    list_filter = ["is_approved", "depth", "created_date"]
    search_fields = ["message", "name", "post__title"]


class CommentReportAdmin(admin.ModelAdmin):
    list_display = ["id", "comment", "reporter", "status", "created_date"]
    list_filter = ["status", "created_date"]
    search_fields = ["reason", "comment__message"]


admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentReport, CommentReportAdmin)


class PostReportAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "reporter", "status", "created_date"]
    list_filter = ["status", "created_date"]
    search_fields = ["reason", "post__title"]


admin.site.register(PostReport, PostReportAdmin)


class PostReactionAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "user", "value", "created_date"]
    list_filter = ["value", "created_date"]


admin.site.register(PostReaction, PostReactionAdmin)
