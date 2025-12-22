from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Profile


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email','is_staff','is_active','is_verified')
    list_filter = ('email','is_staff','is_active','is_verified')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = [
        (
            'Authentication',  
            {
                "fields": ["email", "password"],
            },
        ),
        (
            'permission',  
            {
                "fields": ["is_staff", "is_active",'is_superuser','is_verified'],
            },
        ),
        (
            'group permission',  
            {
                "fields": ["groups", "user_permissions"],
            },
        ),
        (
            'important dates',  
            {
                "fields": ["last_login"],
            },
        )
    ]
    add_fieldsets =((None, {"fields": ["email",'password1','password2','is_staff','is_active','is_superuser','is_verified']}),)


admin.site.register(User,CustomUserAdmin)
admin.site.register(Profile)
