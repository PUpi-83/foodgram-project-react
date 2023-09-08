from django.contrib import admin

# Register your models here.
from .models import Ingredients, Tag, Recipes, IngredientsRecipes, Favorite, ShoppingList


admin.site.register(Ingredients)
admin.site.register(Tag)
admin.site.register(Recipes)
admin.site.register(Favorite)
admin.site.register(ShoppingList)