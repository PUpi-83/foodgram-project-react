from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Tag, Ingredients, Recipes

class RecipesFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), label='Теги')
    author = filters.CharFilter(field_name='author__username', lookup_expr='icontains', label='Автор')
    is_favorite = filters.BooleanFilter(method='filter_is_favorite', label='Избранное')
    is_shopping_list = filters.BooleanFilter(method='filter_is_shopping_list', label='В списке покупок')

    class Meta:
        model = Recipes
        fields = ['tags', 'author', 'is_favorite', 'is_shopping_list']

    def filter_is_favorite(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        else:
            return queryset.exclude(favorites__user=user)

    def filter_is_shopping_list(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_lists__user=user)
        else:
            return queryset.exclude(shopping_lists__user=user)
    
class IngredientsFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', label='Название ингредиента')


    class Meta:
        model = Ingredients
        fields = ['name']