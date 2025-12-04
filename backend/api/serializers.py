import base64
from django.core.files.base import ContentFile
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)
from django.core.validators import RegexValidator
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import AuthenticationFailed

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Subscribe
)
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=1,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')],
    )
    first_name = serializers.CharField(
        required=True,
        max_length=150,
        min_length=1,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150,
        min_length=1,
    )

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')

    def validate(self, attrs):
        if 'username' in attrs and not attrs['username']:
            raise serializers.ValidationError(
                {"username": "This field is required."})
        return attrs


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user, author=obj).exists()
        return False

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return ''


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user

        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError(
                {"current_password": "Wrong password."})

        try:
            validate_password(attrs['new_password'], user)
        except Exception as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)})

        return attrs


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'image', 'name', 'text', 'cooking_time'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.'
            )

        ingredients = []
        ingredient_ids = set()

        for item in value:
            ingredient_id = item.get('id')

            if ingredient_id is None:
                raise serializers.ValidationError(
                    'Укажите ID ингредиента.'
                )

            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиент с ID {ingredient_id} не существует.'
                )

            amount = item.get('amount')
            if amount is None:
                raise serializers.ValidationError(
                    f'Укажите количество для ингредиента с ID {ingredient_id}.'
                )

            try:
                amount = int(amount)
                if amount <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f'Количество для ингредиента с ID {ingredient_id}'
                    f' должно быть положительным числом.'
                )

            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient.name} указан более одного раза.'
                )

            ingredient_ids.add(ingredient_id)
            ingredients.append({
                'ingredient': ingredient,
                'amount': amount
            })

        return ingredients

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise AuthenticationFailed(
                'Пользователь должен быть аутентифицирован.'
            )

        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_avatar(self, obj):
        # Если у вас есть поле avatar в модели User
        if hasattr(obj, 'avatar') and obj.avatar:
            return obj.avatar.url

        # Или если avatar хранится в связанной модели Profile
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url

        # Возвращаем None или URL дефолтного аватара
        return None

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data
