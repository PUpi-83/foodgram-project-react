from drf_extra_fields.fields import Base64ImageField
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    FavoriteList,
    Ingredients,
    RecipeIngredients,
    Recipes,
    ShoppingCart,
    Tags
)
from users.serializers import CustomUserSerializer


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tags
        fields = ("id", "name", "color", "slug")


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    measurement_unit = serializers.CharField(source="measurement_unit.name")

    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для количества ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit.name",
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""
    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    @staticmethod
    def get_ingredients(obj):
        """Получает список ингредиентов с количеством."""
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        """Проверяет, содержится ли данный рецепт в списке избранного."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return FavoriteList.objects.filter(
            user_id=user.id,
            recipe_id=obj.id,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, содержится ли данный рецепт в списке покупок."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user_id=user.id,
                                           recipe_id=obj.id).exists()

    def validate(self, data):
        """Проверяет данные для создания и редактирования рецепта."""
        name = self.initial_data.get("name").strip()
        tags = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")

        data["name"] = name.capitalize()
        data["tags"] = self.validate_tags(tags)
        data["ingredients"] = self.validate_ingredients(ingredients)
        data["author"] = self.context.get("request").user
        return data

    def validate_tags(self, tags):
        """Проверяет теги."""
        if not isinstance(tags, list):
            raise ValidationError(
                "Параметр 'tags' не является списком (list)"
            )
        validated_tags = []
        for tag in tags:
            if not Tags.objects.filter(id=tag):
                raise ValidationError(f"Тег {tag} не существует")
            validated_tags.append(tag)
            if tag not in validated_tags:
                raise ValidationError(f"Тег {tag} уже был передан")
        return validated_tags

    def validate_ingredients(self, ingredients):
        """Проверяет ингредиенты."""
        if not isinstance(ingredients, list):
            raise ValidationError(
                "Параметр 'ingredients' не является списком (list)"
            )
        checked_ingredients = []
        for ingredient in ingredients:
            if not Ingredients.objects.filter(id=ingredient.get("id")):
                raise ValidationError(
                    f"Ингредиент с 'id' {ingredient.get('id')} не существует"
                )
            amount = ingredient.get("amount")
            if (not str(amount).isdecimal() or not (
                    settings.MIN_POSITIVE_AMOUNT < int(amount)
                    <= settings.MAX_POSITIVE_AMOUNT)):
                raise ValidationError(
                    f"Значение amount '{ingredient.get('amount')}' "
                    "должно быть положительным числом от 1 до 32767"
                )
            checked_ingredients.append(
                {"id": ingredient.get("id"), "amount": amount},
            )
        return checked_ingredients

    @staticmethod
    def create_tags(tags, recipe):
        """Создает связь между тегами и рецептом."""
        for tag in tags:
            recipe.tags.add(tag)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """Создает связь между ингредиентами и рецептом."""
        recipe_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredients, pk=ingredient["id"]),
                amount=ingredient.get("amount"),
            )
            for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Создает рецепт."""
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Редактирует рецепт."""
        instance.tags.clear()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop("tags"), instance)
        self.create_ingredients(validated_data.pop("ingredients"), instance)
        return super().update(instance, validated_data)


class RecipesShortSerializer(RecipesSerializer):
    """Сериализатор для сокращенного вывода данных модели Recipes."""

    class Meta:
        model = Recipes
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = ("__all__",)


class BaseListSerializer(serializers.ModelSerializer):
    """Общий базовый сериализатор для моделей FavoriteList и ShoppingCart."""
    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipesShortSerializer(instance.recipe, context=context).data


class FavoriteListSerializer(BaseListSerializer):
    """Сериализатор для модели FavoriteList."""

    class Meta:
        model = FavoriteList
        fields = ("id", "user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]


class ShoppingCartSerializer(BaseListSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = ("id", "user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]
