from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredients, IngredientsRecipes, Recipes,
                            ShoppingList, Tag)
from users.models import CustomUser