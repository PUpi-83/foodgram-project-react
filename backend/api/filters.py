from django_filters import AllValuesMultipleFilter
from django_filters.rest_framework import BooleanFilter, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipes


class IngredientsSearchFilter(SearchFilter):
    """Фильтрация ингредиента по имени."""

    search_param = "name"


class RecipesFilter(FilterSet):
    """Фильтр рецепта."""

    tags = AllValuesMultipleFilter(
        field_name="tags__slug",
    )
    is_favorited = BooleanFilter(
        method="filter_is_favorited",
    )
    is_in_shopping_cart = BooleanFilter(
        method="filter_is_in_shopping_cart",
    )

    class Meta:
        model = Recipes
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов в избранном."""
        if value:
            return queryset.filter(favorite_list_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов в списке покупок."""
        if value:
            return queryset.filter(shopping_cart_recipe__user=self.request.user)
        return queryset
