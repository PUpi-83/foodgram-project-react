from django.contrib import admin

from .models import Ingredient, Tag, Recipe, AmountIngredients, Favorite, ShoppingCart


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(AmountIngredients)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)