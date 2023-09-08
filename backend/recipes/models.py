from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator, RegexValidator)

from users.models import CustomUser


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиентов'
    )
    unit_of_measurement = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель для тегов"""
    name = models.CharField(
        max_length=200,
        verbose_name = 'Теги для обозначения'
    )
    hex_color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6})$',
        message='Цветовой код должен быть в формате HEX (#RRGGBB)',
        code='invalid_hex_color'
    )
    color_code = models.CharField(
        max_length=7,
        verbose_name='Цветовой код',
        unique=True,
        validators=[hex_color_validator],
    )
    
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель для рецепта"""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name = 'Создатель рецепта')
    
    title = models.CharField(
        max_length=200,
        verbose_name="Название рецепта"
        )

    image = models.ImageField(
        upload_to='recipe/image/',
        verbose_name = 'Картинка'
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Описание рецепта'
        )
    ingredients = models.ManyToManyField(
        Ingredients, 
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    cooking_time = models.TimeField(
        validators=(MinValueValidator(5, message="На приготовление блюда должно уйти не меньше 5 минут"),
                    MaxValueValidator(48, message="Максимальное время приготовления не должно превышать 2 суток!")),
        verbose_name='Время на приготовление блюда'
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    servings = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Должна получиться хотя бы одна порция"),
                     MaxValueValidator(5, message="Максимальное количество порций 10, не больше")],
        verbose_name='Количество порций'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class IngredientsRecipes(models.Model):
    """Связывающая модель для ингридиентов и рецептов"""
    recipes = models.ForeignKey(
        Recipes,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="ingredients_recipes"
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name="Название ингридиента",
        related_name="recipes_ingredients"
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ['-id']
    
    def __str__(self):
        return f'{self.recipes.title} - {self.ingredient.name}'



class FavoriteShoppingList(models.Model):
    """Абстрактная модель для избранного и списка покупок"""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    class Meta:
        abstract = True
        verbose_name = "Избранный элемент"
        verbose_name_plural = "Избранные элементы"

    def __str__(self):
        return f"{self.author.username} - {self.recipes.title}"

class Favorite(FavoriteShoppingList):
    """Модель для избранных рецептов"""
    class Meta(FavoriteShoppingList.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

class ShoppingList(FavoriteShoppingList):
    """Модель для списка покупок"""
    class Meta(FavoriteShoppingList.Meta):
        verbose_name = "Элемент списка покупок"
        verbose_name_plural = "Элементы списка покупок"