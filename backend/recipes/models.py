from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator, RegexValidator)

from users.models import CustomUser


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиентов'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
    
    def __str__(self):
         return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель для тегов"""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name = 'Название тэга'
    )
    hex_color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6})$',
        message='Цветовой код должен быть в формате HEX (#RRGGBB)',
        code='invalid_hex_color'
    )
    color = ColorField(
        max_length=7,
        format='hex',
        verbose_name='Цветовой код',
        unique=True,
        validators=[hex_color_validator],
    )
    
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=150
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецепта"""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name = 'Создатель рецепта')
    
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта"
        )

    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name = 'Картинка'
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient, 
        verbose_name='Ингридиенты',
        through='AmountIngredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(5, message="На приготовление блюда должно уйти не меньше 5 минут"),
                    MaxValueValidator(2880, message="Максимальное время приготовления не должно превышать 2 суток!")),
        verbose_name='Время приготовления блюда'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class FavoriteShoppingCart(models.Model):
    """Абстрактная модель для избранного и списка покупок"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    class Meta:
        abstract = True
        verbose_name = "Избранный элемент"
        verbose_name_plural = "Избранные элементы"

    def __str__(self):
        return f"{self.user}, {self.recipes}"

class Favorite(FavoriteShoppingCart):
    """Модель для избранных рецептов"""
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

class ShoppingCart(FavoriteShoppingCart):
    """Модель для списка покупок"""
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"


class AmountIngredients(models.Model):
    """Модель ингридиентов в рецепте"""
    recipe = models.ForeignKey(Recipe, 
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message='В рцепте должен быть минимум 1 ингредиет'),
                    MaxValueValidator(50,message='В рцепте должно быть максимум 50 ингредиетов')],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return(
            f'{self.ingredient.name}, {self.ingredient.measurement_unit}'
            f' - {self.amount} ')