from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status

from recipes.models import Recipes

from .models import CustomUser, Follow


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор регистрации."""

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
    """Сериализатор авторизированного пользовател."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор кратких сведений о рецепте."""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(CustomUserSerializer):
    """Сериализатор подписок пользователя."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user

        if author == user:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail="Вы уже подписаны на этого пользователя",
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data
