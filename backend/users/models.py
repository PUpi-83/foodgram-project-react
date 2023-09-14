from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import UniqueConstraint
from django.db import models

class CustomUser(AbstractUser):
    """Модель пользователя"""
    first_name = models.CharField(
        max_length=200,
        verbose_name= "Имя"
    )
    last_name = models.CharField(
        max_length=200,
        verbose_name="Фамилия"
    )
    username = models.CharField(
        max_length=200,
        verbose_name="Ник",
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )
    email = models.EmailField(
        max_length=250,
        verbose_name="Почта",
        unique = True
    )

    class Meta:
        ordering = ('username', )
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Follow(models.Model):
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                  verbose_name='Подписка',
                                  related_name='following')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower')

    class Meta:
        verbose_name = 'Подписки'
        UniqueConstraint(fields=['following', 'user'], name='follow_unique')

    def __str__(self):
        return f"{self.user} подписан на {self.following}"

