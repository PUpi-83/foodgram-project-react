from django.contrib.auth.models import AbstractUser
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
    login = models.CharField(
        max_length=200,
        verbose_name="Ник",
         unique=True
    )
    email = models.EmailField(
        max_length=250,
        verbose_name="Почта",
        unique = True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username 


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name='following'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

