from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Модель пользователя."""

    password = models.CharField(_("password"), max_length=150)
    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    @property
    def is_admin(self):
        return self.is_staff

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username.capitalize()


class Follow(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                name="unique_follow",
                fields=["user", "author"],
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
