from django.contrib import admin

from .models import (
    FavoriteList,
    Ingredients,
    MeasureUnits,
    RecipeIngredients,
    Recipes,
    RecipeTags,
    ShoppingCart,
    Tags
)


@admin.register(MeasureUnits)
class MeasureUnitsAdmin(admin.ModelAdmin):
    """Регистрация модели количества ингреиента в админке."""
    model = MeasureUnits


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Регистрация модели ингредиентов в админке."""
    model = Ingredients
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    list_editable = ("measurement_unit",)
    empty_value_display = "-отсутствует-"


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Регистрация модели рецепта в админке."""
    class TagsInline(admin.TabularInline):
        model = RecipeTags
        extra = 1

    class IngredientsInline(admin.TabularInline):
        model = RecipeIngredients
        extra = 1

    model = Recipes
    inlines = (TagsInline, IngredientsInline)
    list_display = ("name", "author", "favorite_count")
    readonly_fields = ("favorite_count",)
    search_fields = ("name",)
    list_filter = ("author", "name", "tags")
    filter_horizontal = ("tags",)
    empty_value_display = "-отсутствует-"

    def favorite_count(self, obj):
        """Метод для вычисления и отображения
        количества добавлений рецепта в избранное."""
        return FavoriteList.objects.filter(recipe=obj).count()

    favorite_count.short_description = "Количество добавлений в избранное"


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """Регистрация модели тегов в админке."""
    model = Tags
    list_display = ("name", "color", "slug")
    search_fields = ("name",)


@admin.register(FavoriteList)
class FavoriteListAdmin(admin.ModelAdmin):
    """Регистрация модели избранных рецептов в админке."""
    model = FavoriteList
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Регистрация модели списка покупок в админке."""
    model = ShoppingCart
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")
