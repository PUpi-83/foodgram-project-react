from rest_framework import serializers, status
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField, IntegerField
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag, AmountIngredients)
from users.models import CustomUser, Follow

class CustomUserSerializer(UserSerializer):
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

class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""
    
    class Meta:
        model = Ingredient
        fields = ('id', 'name',
            'measurement_unit')


class AmountIngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор для количества игредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            read_only=True
    )
    name = serializers.SlugRelatedField(slug_field='name',
                                        source='ingredient',
                                        read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit',
        source='ingredient', read_only=True
    )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = AmountIngredients
        fields = ("id", "name", "measurement_unit", "amount")

class AddToAmountIngredientsSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = AmountIngredients
        fields = ('amount', 'id')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов"""

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")



class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор для списка покупок"""

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для созданного рецепта"""
    tags = TagSerializer(read_only=False, many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart", 
                  "image", "text", 'name', "cooking_time")

    def get_ingredients(self, obj):
        ingredients = AmountIngredients.objects.filter(recipe=obj)
        serializer = AmountIngredientsSerializer(ingredients, many=True)
        return serializer.data

    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()

class RecipeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)
        
class CreateRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    ingredients = AddToAmountIngredientsSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
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
    
    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Число игредиентов должно быть больше 0')
                })
        return data
    
    @transaction.atomic
    def create_ingredients(self, ingredients, recipe):
        AmountIngredients.objects.bulk_create(
            [AmountIngredients(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance


class SubscribeSerializer(UserSerializer):
    """Сериализатор для подписки."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes_count', 'recipes')
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


class FollowSerializer(serializers.ModelSerializer):

    following = serializers.SlugRelatedField(
        slug_field='id',
        queryset=CustomUser.objects.all(),
    )
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=CustomUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Такая подписка уже существует'
            )
        ]


class FollowCartSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, user):
        current_user = self.context.get('current_user')
        other_user = user.following.all()
        if user.is_anonymous:
            return False
        if other_user.count() == 0:
            return False
        if Follow.objects.filter(user=user, following=current_user).exists():
            return True
        return False

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        request = self.context.get('request')
        return RecipeImageSerializer(
            recipes, many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()