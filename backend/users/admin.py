from django.contrib import admin
from .models import Follow, CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Регистрация модели пользователя в админке."""
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
    """Регистрация модели подписки в админке."""
    model = Follow
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")
