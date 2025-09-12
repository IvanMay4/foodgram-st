from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils.encoding import smart_str

from .models import Recipe, Ingredient, User, Follow, Favorite, ShoppingCart
from .serializers import (
    RecipeSerializer, RecipeCreateSerializer, IngredientSerializer,
    UserSerializer, CurrentUserProfileSerializer, FollowSerializer,
    FavoriteSerializer, ShoppingCartSerializer
)
from .pagination import CustomPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def recipes_list(self, request):
        user_recipes = Recipe.objects.filter(
            author=request.user).order_by('-pub_date')
        page = self.paginate_queryset(user_recipes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(user_recipes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(Favorite.objects.get(
                user=user, recipe=recipe), context={'request': request})
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=204)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(ShoppingCart.objects.get(
                user=user, recipe=recipe), context={'request': request})
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=204)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_recipes = ShoppingCart.objects.filter(
            user=user).values_list('recipe', flat=True)
        recipes = Recipe.objects.filter(id__in=shopping_cart_recipes)

        ingredients_dict = {}
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount
                unit = ingredient.measurement_unit

                if ingredient.name in ingredients_dict:
                    if unit in ingredients_dict[ingredient.name]:
                        ingredients_dict[ingredient.name][unit] += amount
                    else:
                        ingredients_dict[ingredient.name][unit] = amount
                else:
                    ingredients_dict[ingredient.name] = {unit: amount}

        output_lines = []
        output_lines.append("Список покупок:\n")
        for name, units in ingredients_dict.items():
            for unit, total_amount in units.items():
                output_lines.append(f"- {name} ({unit}) — {total_amount}")

        file_content = "\n".join(output_lines)

        response = HttpResponse(smart_str(file_content),
                                content_type='text/plain')
        response['Content-Disposition'] =\
            'attachment; filename="shopping_list.txt"'
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    # Кастомное действие для получения профиля конкретного пользователя
    @action(detail=True, methods=['get'], url_path='recipes',
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def user_recipes(self, request, pk=None):
        """
        Возвращает список рецептов конкретного пользователя.
        """
        user = self.get_object()
        user_recipes = user.recipes.all().order_by('-pub_date')
        page = self.paginate_queryset(user_recipes)
        if page is not None:
            serializer = RecipeSerializer(page, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(user_recipes, many=True,
                                      context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        user_to_subscribe = self.get_object()
        user = request.user

        if user == user_to_subscribe:
            return Response(
                {'detail': 'Вы не можете подписаться на самого себя.'},
                status=400
            )

        if request.method == 'POST':
            Follow.objects.get_or_create(
                user=user,
                following=user_to_subscribe
            )
            serializer = FollowSerializer(Follow.objects.get(
                user=user,
                following=user_to_subscribe),
                context={'request': request}
            )
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            Follow.objects.filter(user=user,
                                  following=user_to_subscribe).delete()
            return Response(status=204)


class CurrentUserViewSet(viewsets.ModelViewSet):
    serializer_class = CurrentUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'], url_path='subscriptions',
            serializer_class=UserSerializer)
    def subscriptions(self, request):
        user = request.user
        following_users = User.objects.filter(following__user=user)
        page = self.paginate_queryset(following_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(following_users, many=True,
                                         context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='favorite')
    def favorite_recipes(self, request):
        user = request.user
        favorite_recipes = Recipe.objects.filter(favorite_recipes__user=user)
        page = self.paginate_queryset(favorite_recipes)
        if page is not None:
            serializer = RecipeSerializer(page, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(favorite_recipes, many=True,
                                      context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='shopping_cart')
    def shopping_cart_recipes(self, request):
        user = request.user
        shopping_cart_recipes = Recipe.objects.filter(shopping_cart__user=user)
        page = self.paginate_queryset(shopping_cart_recipes)
        if page is not None:
            serializer = RecipeSerializer(page, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(shopping_cart_recipes, many=True,
                                      context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['patch'],
            serializer_class=CurrentUserProfileSerializer)
    def update_avatar(self, request):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
