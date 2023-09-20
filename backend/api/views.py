from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (FavoriteList, Ingredients, RecipeIngredients,
                            Recipes, ShoppingCart, Tags)

from .filters import IngredientsSearchFilter, RecipesFilter
from .pagination import CustomPageNumberPagination
from .permissions import AdminOrAuthorOrReadOnly
from .reports import create_recipe_shopping_list
from .serializers import (FavoriteListSerializer, IngredientsSerializer,
                          RecipesSerializer, ShoppingCartSerializer,
                          TagsSerializer)


class TagsViewSet(ReadOnlyModelViewSet):
    """Viewset для модели Tags."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Viewset для модели Ingredients."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ("^name",)
    pagination_class = None


class RecipesViewSet(ModelViewSet):
    """Viewset для модели Recipes."""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (AdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = CustomPageNumberPagination

    @staticmethod
    def handle_action(request, pk, serializers, model):
        if request.method == 'POST':
            data = {"user": request.user.id, "recipe": pk}
            serializer = serializers(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipes, id=pk)
            model_obj = get_object_or_404(model, user=user, recipe=recipe)
            model_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.handle_action(
            request=request, pk=pk,
            serializers=FavoriteListSerializer,
            model=FavoriteList
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.handle_action(
            request=request, pk=pk,
            serializers=ShoppingCartSerializer,
            model=ShoppingCart
        )

    @action(
        methods=("GET",),
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shopping_cart_recipe__user=request.user,
            )
            .values_list(
                "ingredient__name",
                "ingredient__measurement_unit__name",
            )
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        return create_recipe_shopping_list(ingredients)
