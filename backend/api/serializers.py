from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField, IntegerField
from recipes.models import (Favorite, Ingredients, IngredientsRecipes, Recipes,
                            ShoppingList, Tag)
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
        fields = ("id", "first_name", "last_name", "email", 'username', 'is_subscribed')
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            current_user = request.user
            is_subscribed = current_user.is_subscribed_to(obj)
            return is_subscribed
        return False

class IngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор связи ингридиентов и рецепта """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'name', 'unit_of_measurement')

class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для нового пользователя"""

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", 'username', "email", "password")

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов"""

    class Meta:
        model = Favorite
        fields = ("user", "recipes")

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipes')
        if Favorite.objects.filter(user=user, recipes=recipe).exists():
            raise serializers.ValidationError("Этот рецепт уже в избранном у пользователя.")
        return data

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ("id", "name", "color_code", "slug")

class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""
    
    class Meta:
        model = Ingredients
        fields = ("id", "name", "unit_of_measurement")

class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShoppingList
        fields = ("author", "recipes")

    def validate(self, data):
        author = data.get('author')
        recipes = data.get('recipes')
        if ShoppingList.objects.filter(author=author, recipes__in=recipes).exists():
            raise serializers.ValidationError("Один или несколько рецептов уже находятся в вашем списке покупок.")
        return data

class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для созданного рецепта"""
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def ingredients(self, obj):
        ingredients_queryset = IngredientsRecipes.objects.filter(recipe=obj)
        ingredients_data = IngredientsSerializer(ingredients_queryset, many=True).data
        return ingredients_data
    
    def get_favotite(self, obj):
        user = self.context.get('request')
        if user.is_anonymous:
            return False
        return user.favorite_recipes.filter(pk=obj.pk).exists()
    
    def get_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(pk=obj.pk).exists()

    class Meta:
        model = Recipes
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart", 
                  "image", "text", "cooking_time")
        
class CreateRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    author = UserSerializer(read_only=True, many=False)
    image = Base64ImageField()
    cooking_time = IntegerField()
    
    class Meta:
        model = Recipes
        fields = ("id", "tags", "author", "ingredients",
                  "title","image", "text", "cooking_time")
    
    def validate_tags_1(self, tags):
        if len(tags) < 1:
            raise serializers.ValidationError("Должен быть выбран как минимум один тег")
        return tags
    
    def validate_tags_2(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError("Такого тега не найдено")
        return tags
    
    def validate_cooking_time(self, cooking_time):
        if cooking_time < 5:
            raise serializers.ValidationError("Время приготовления должно быть не менее 5 минут")
        return cooking_time
    
    def validation_title(self, title):
        if len(title) < 3:
            raise serializers.ValidationError("Название рецепта должно содержать как минимум 3 символа")
        return title
    
    def create_ingredients(recipes, ingredients):
        for ingredient in ingredients:
            ingredient, created = Ingredients.objects.get_or_create(id=ingredients['id'])
            recipes.ingredients.add(ingredient)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        self.update_tags(instance, tags)
        self.update_ingredients(instance, ingredients)
        return instance

    def update_tags(self, instance, tags):
        instance.tags.clear()
        instance.tags.add(*tags)

    def update_ingredients(self, instance, ingredients):
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance, ingredients=ingredients)


class SubscribeSerializer(UserSerializer):
    """Сериализатор для подписки."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        user = self.context['request'].user
        target_user_id = data.get('target_user_id')
        try:
            target_user = CustomUser.objects.get(pk=target_user_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким ID не существует")
        if user == target_user:
            raise serializers.ValidationError("Вы не можете подписаться на самих себя")
        return data
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = Recipes.objects.filter(user=obj)
        serializer = RecipesSerializer(recipes, many=True)
        return serializer.data