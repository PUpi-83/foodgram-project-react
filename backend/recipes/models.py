from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.settings import (AMOUNT, POSITIVE_NUMBER_1,
                               TIME, TIME_1, LENGTH_NAME,
                               LENGTH_SLUG)

User = get_user_model()


class Tags(models.Model):
    """Модель для тегов."""

    name = models.CharField("Имя", max_length=LENGTH_NAME)
    color = ColorField("Цвет", default='#FF0000')
    slug = models.SlugField(max_length=LENGTH_SLUG, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class MeasureUnits(models.Model):
    """Модель единиц измерения ингредиентов."""

    name = models.CharField("Наименование", max_length=LENGTH_NAME,
                            unique=True)

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов."""

    name = models.CharField("Название", max_length=LENGTH_NAME)
    measurement_unit = models.ForeignKey(
        MeasureUnits,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Единицы измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField("Название рецепта", max_length=LENGTH_NAME)
    image = models.ImageField(
        "Изображение", upload_to="images", null=True, default=None
    )
    text = models.TextField("Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredients,
        through="RecipeIngredients",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tags,
        through="RecipeTags",
        related_name="recipes",
        verbose_name="Теги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (минут)",
        validators=[MinValueValidator(TIME,
                                      message='Время не меньше 1 минуты'),
                    MaxValueValidator(TIME_1,
                                      message='Время не больше 1000 минут')],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Связывающая модель рецептов с ингредиентами."""

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=(
            MinValueValidator(AMOUNT, message='Минимальное количество - 1'),
            MaxValueValidator(POSITIVE_NUMBER_1,
                              message='Максимальное количество - 32767')
        ),
    )

    class Meta:
        verbose_name = "Ингредиенты рецепта"
        verbose_name_plural = "Ингредиенты рецептов"
        constraints = [
            models.UniqueConstraint(
                name="unique_recipe_ingredients",
                fields=["recipe", "ingredient"],
            ),
        ]


class RecipeTags(models.Model):
    """Связывающая модель рецептов с тегами."""

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Теги рецепта"
        verbose_name_plural = "Теги рецептов"
        constraints = [
            models.UniqueConstraint(
                name="unique_recipe_tags",
                fields=["recipe", "tag"],
            ),
        ]


class FavoriteList(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_list_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite_list_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                name="unique_favorite_list",
                fields=["user", "recipe"],
            ),
        ]

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в список избранного"


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                name="unique_shopping_cart",
                fields=["user", "recipe"],
            ),
        ]

    def __str__(self):
        return (f"{self.user.username} добавил"
                f"{self.recipe.name} в список покупок")
