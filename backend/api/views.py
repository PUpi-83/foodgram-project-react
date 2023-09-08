from django.db.models import Sum
from collections import defaultdict
from fpdf import FPDF
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from recipes.models import Ingredients, Tag, Recipes, IngredientsRecipes, Favorite, ShoppingList
from users.models import CustomUser, Follow
from api.filtres import RecipesFilter, IngredientsFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import UserSerializer, SubscribeSerializer, FavoriteSerializer, TagSerializer, ShoppingListSerializer, RecipesSerializer, CreateRecipesSerializer, IngredientsSerializer


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(detail=True, 
            methods=['post'],
            permission_classes=[IsAuthenticated])
    
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)
        if user == author:
            return Response({'detail': 'Вы не можете подписаться сами на себя'}, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({'detail': 'Вы уже подписаны на этого автора.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription = Follow.objects.create(user=user, author=author)
        return Response({'detail': 'Подписка на автора прошла упешно.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, 
            methods=['delete'],
            permission_classes=[IsAuthenticated])
    
    def unsubscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        if user == author:
            return Response({'detail': 'You cannot unsubscribe from yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            subscription = Follow.objects.get(user=user, author=author)
        except Follow.DoesNotExist:
            return Response({'detail': 'You are not subscribed to this author.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response({'detail': 'You have successfully unsubscribed from this author.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, 
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        serializer = SubscribeSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    filter_backends = (IngredientsFilter,)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipesSerializer
    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_recipe_action(self, model, user, pk, action):
        recipe = get_object_or_404(Recipes, id=pk)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        
        if created and action == 'add':
            status_code = status.HTTP_201_CREATED
        elif not created and action == 'delete':
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'errors': 'Рецепт уже добавлен/удален!'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RecipesSerializer(recipe)
        return Response(serializer.data, status=status_code)

    def add_to(self, model, user, pk):
        return self.perform_recipe_action(model, user, pk, 'add')

    def delete_from(self, model, user, pk):
        return self.perform_recipe_action(model, user, pk, 'delete')

    def download_shopping_list(self, request, pk=None):
        if pk is not None:
            recipes = get_object_or_404(Recipes, pk=id)
            ingredients = IngredientsRecipes.objects.filter(recipe=recipes)
            shopping_list = defaultdict(float)
            for ingredient in ingredients:
                shopping_list[ingredient.ingredient.name] += ingredient.amount
            output_format = request.query_params.get('format', 'txt')
            if output_format == 'txt':
                response = HttpResponse(content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{recipes.title}_shopping_list.txt"'
                for ingredient, quantity in shopping_list.items():
                    response.write(f'{ingredient} — {quantity} г\n')
                return response
            elif output_format == 'pdf':
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for ingredient, quantity in shopping_list.items():
                    pdf.cell(200, 10, txt=f'{ingredient} — {quantity} г', ln=True)
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{recipes.title}_shopping_list.pdf"'
                pdf.output(response, dest='S')
                return response
            else:
                return Response({'detail': 'Неподдерживаемый формат файла'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Рецепт не найден'}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=True, 
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = self.get_object()
        user = request.user
        try:
            favorite = Favorite.objects.get(user=user, recipe=recipe)
            favorite.delete()
            return Response({'detail': 'Recipe removed from favorites'}, status=204)
        except Favorite.DoesNotExist:
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            return Response({'detail': 'Recipe added to favorites'}, status=201)


