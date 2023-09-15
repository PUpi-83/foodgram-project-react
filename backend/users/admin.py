from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    list_filter = ("username", "email")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")
