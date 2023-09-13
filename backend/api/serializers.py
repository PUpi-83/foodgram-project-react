from rest_framework import serializers, status
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField, IntegerField
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag, AmountIngredients)
from users.models import CustomUser

class UserSerializer(UserSerializer):
    """Сериализатор для текущего пользователя"""
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "email", "username", "is_subscribed")
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()
    
class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для нового пользователя"""

    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "username", "email", "password")

class AmountIngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор для количества игредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    unit_of_measurement = serializers.ReadOnlyField(
        source='ingredient.unit_of_measurement'
    )

    class Meta:
        model = AmountIngredients
        fields = ("id", "name", "unit_of_measurement", 'amount')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов"""

    class Meta:
        model = Favorite
        fields = ("user", "recipe",)

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")

class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""
    
    class Meta:
        model = Ingredient
        fields = ("id", "name", "unit_of_measurement",)

class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ("author", "recipe",)

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для созданного рецепта"""
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    image = Base64ImageField(max_length=None)
    ingredients = AmountIngredientsSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients_queryset = AmountIngredients.objects.filter(recipe=obj)
        ingredients_data = AmountIngredients(ingredients_queryset, many=True).data
        return ingredients_data
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart", 
                  "image", "text", 'name', "cooking_time")
        
class CreateRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    ingredients = AmountIngredientsSerializer(many=True,)
    author = UserSerializer(read_only=True, many=False)
    image = Base64ImageField(max_length=None)
    cooking_time = IntegerField()
    
    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "name","image", "text", "cooking_time")
    
    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError("Такого тега не найдено")
        return tags
    
    def validate_cooking_time(self, cooking_time):
        if cooking_time < 5:
            raise serializers.ValidationError("Время приготовления должно быть не менее 5 минут")
        return cooking_time
    
    def validate_name(self, name):
        if len(name) < 3:
            raise serializers.ValidationError("Название рецепта должно содержать как минимум 3 символа")
        return name
    
    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствуют ингридиенты')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальны')
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента больше 0')
        return ingredients
    
    def create_ingredients(self, ingredients, recipe):
        with transaction.atomic():
            amount_ingredients = []
            for ingredient_data in ingredients:
                amount_ingredients.append(
                    AmountIngredients(
                        ingredient=ingredient_data.pop('id'),
                        amount=ingredient_data.pop('amount'),
                        recipe=recipe,
                )
            )

            AmountIngredients.objects.bulk_create(amount_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe,
                                ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        AmountIngredients.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    

class SubscribeSerializer(UserSerializer):
    """Сериализатор для подписки."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(CustomUser, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(user=obj)
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data
    