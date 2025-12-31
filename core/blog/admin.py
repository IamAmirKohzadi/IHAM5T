from django.contrib import admin
from .models import Post,Category
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ['author','title','status','counted_view','categories_list','created_date']
    filter_horizontal = ['categories']

    def categories_list(self, obj):
        return ", ".join(obj.categories.values_list("name", flat=True))
    categories_list.short_description = "Categories"

    
admin.site.register(Post,PostAdmin)
admin.site.register(Category)
