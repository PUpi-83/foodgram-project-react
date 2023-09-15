from django.contrib import admin

from .models import (Cart, Ingredients, MeasureUnits, RecipeIngredients,
                     Recipes, RecipeTags, Tags, Wishlist)


@admin.register(MeasureUnits)
class MeasureUnitsAdmin(admin.ModelAdmin):
    model = MeasureUnits


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    model = Ingredients
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    list_editable = ("measurement_unit",)
    empty_value_display = "-отсутствует-"


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    class TagsInline(admin.TabularInline):
        model = RecipeTags
        extra = 1

    class IngredientsInline(admin.TabularInline):
        model = RecipeIngredients
        extra = 1

    model = Recipes
    inlines = (TagsInline, IngredientsInline)
    list_display = ("name", "author")
    search_fields = ("name",)
    list_filter = ("author", "name", "tags")
    filter_horizontal = ("tags",)
    empty_value_display = "-отсутствует-"


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    model = Tags
    list_display = ("name", "color", "slug")
    search_fields = ("name",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    model = Wishlist
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")
