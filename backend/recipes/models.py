from django.contrib.auth import get_user_model
from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Tags(models.Model):
    """Модель для тегов."""

    name = models.CharField("Имя", max_length=30)
    color = ColorField("Цвет", default='#FF0000')
    slug = models.SlugField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class MeasureUnits(models.Model):
    """Модель единиц измерения ингредиентов."""

    name = models.CharField("Наименование", max_length=20, unique=True)

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов."""

    name = models.CharField("Название", max_length=100)
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
    name = models.CharField("Название рецепта", max_length=200)
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
            MinValueValidator(1, message='Минимальное количество - 1'),
            MaxValueValidator(32767, message='Максимальное количество - 32767')
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
        related_name='favoritelist_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favoritelist_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                name="unique_favoritelist",
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
        related_name='shoppingcart_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shoppingcart_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                name="unique_shoppingcart",
                fields=["user", "recipe"],
            ),
        ]

    def __str__(self):
        return f"{self.user.name} добавил {self.recipe.name} в список покупок"
