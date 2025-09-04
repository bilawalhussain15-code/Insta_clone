from django.contrib import admin
from .models import CustomUser, Post, Like, Comment, Follow
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("name", "bio", "gender", "profile_picture", "followers")}),
    )


admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
