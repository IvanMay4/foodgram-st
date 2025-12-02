from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Subscribe, User
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    ShortRecipeSerializer, SubscribeSerializer, UserCreateSerializer, CustomUserSerializer
)


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all().order_by('id')
#     pagination_class = CustomPagination
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny,)
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         print(context)
#         return context
#
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve', 'create']:
#             return [AllowAny()]
#         return [IsAuthenticated()]
#
#     @action(
#         detail=False,
#         methods=['get'],
#         permission_classes=[IsAuthenticated]
#     )
#     def me(self, request):
#         serializer = self.get_serializer(request.user)
#         return Response(serializer.data)
#
#     @action(
#         detail=False,
#         methods=['get'],
#         permission_classes=[IsAuthenticated],
#         url_path='subscriptions'
#     )
#     def subscriptions(self, request):
#         user = request.user
#         queryset = Subscribe.objects.filter(user=user)
#         pages = self.paginate_queryset(queryset)
#         serializer = SubscribeSerializer(
#             pages, many=True, context={'request': request}
#         )
#         return self.get_paginated_response(serializer.data)
#
#     @action(
#         detail=True,
#         methods=['post', 'delete'],
#         permission_classes=[IsAuthenticated]
#     )
#     def subscribe(self, request, pk=None):
#         author = get_object_or_404(User, id=pk)
#         user = request.user
#
#         if request.method == 'POST':
#             if user == author:
#                 return Response(
#                     {'errors': 'Нельзя подписаться на самого себя'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             if Subscribe.objects.filter(user=user, author=author).exists():
#                 return Response(
#                     {'errors': 'Вы уже подписаны на этого автора'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             subscribe = Subscribe.objects.create(user=user, author=author)
#             serializer = SubscribeSerializer(
#                 subscribe, context={'request': request}
#             )
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         if request.method == 'DELETE':
#             subscribe = get_object_or_404(
#                 Subscribe, user=user, author=author
#             )
#             subscribe.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
class UserViewSet(DjoserUserViewSet):
    """
    ViewSet для работы с пользователями.
    Наследуется от Djoser UserViewSet.
    """
    queryset = User.objects.all()

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action == 'create':
            from .serializers import UserCreateSerializer
            return UserCreateSerializer
        elif self.action == 'me':
            return CustomUserSerializer
        return CustomUserSerializer

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated]
    # )
    # def subscribe(self, request, id=None):
    #     """
    #     Подписаться или отписаться от пользователя.
    #     """
    #     user = request.user
    #     author = get_object_or_404(User, id=id)
    #
    #     if request.method == 'POST':
    #         # Проверяем, не пытается ли пользователь подписаться на себя
    #         if user == author:
    #             return Response(
    #                 {'errors': 'Нельзя подписаться на самого себя'},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #
    #         # Проверяем, существует ли уже подписка
    #         if Follow.objects.filter(user=user, author=author).exists():
    #             return Response(
    #                 {'errors': 'Вы уже подписаны на этого пользователя'},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #
    #         # Создаем подписку
    #         Follow.objects.create(user=user, author=author)
    #
    #         # Возвращаем данные автора
    #         serializer = FollowSerializer(
    #             author,
    #             context={'request': request}
    #         )
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    #     elif request.method == 'DELETE':
    #         # Удаляем подписку, если она существует
    #         subscription = Follow.objects.filter(user=user, author=author)
    #         if subscription.exists():
    #             subscription.delete()
    #             return Response(status=status.HTTP_204_NO_CONTENT)
    #
    #         return Response(
    #             {'errors': 'Вы не подписаны на этого пользователя'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    # @action(
    #     detail=False,
    #     permission_classes=[IsAuthenticated]
    # )
    # def subscriptions(self, request):
    #     """
    #     Получить список подписок текущего пользователя.
    #     """
    #     user = request.user
    #     # Получаем всех авторов, на которых подписан пользователь
    #     authors = User.objects.filter(following__user=user)
    #
    #     # Пагинация
    #     page = self.paginate_queryset(authors)
    #     if page is not None:
    #         serializer = FollowSerializer(
    #             page,
    #             many=True,
    #             context={'request': request}
    #         )
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = FollowSerializer(
    #         authors,
    #         many=True,
    #         context={'request': request}
    #     )
    #     return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                ShoppingCart, user=user, recipe=recipe
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = user.shopping_cart.all()

        # Собираем ингредиенты из всех рецептов в корзине
        ingredients = {}
        for item in shopping_cart:
            for recipe_ingredient in item.recipe.recipe_ingredients.all():
                key = (recipe_ingredient.ingredient.name,
                       recipe_ingredient.ingredient.measurement_unit)
                if key in ingredients:
                    ingredients[key] += recipe_ingredient.amount
                else:
                    ingredients[key] = recipe_ingredient.amount

        # Формируем текстовый файл
        shopping_list = "Список покупок:\n\n"
        for (name, unit), amount in ingredients.items():
            shopping_list += f"{name} ({unit}) - {amount}\n"

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_list.txt"'
        return response


@api_view(['PUT'])
def update_user_avatar(request):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'Avatar file is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    avatar_file = request.FILES['avatar']
    request.user.avatar = avatar_file
    request.user.save()

    return Response({
        'avatar': request.user.avatar.url
    }, status=status.HTTP_200_OK)


# class CustomObtainAuthToken(ObtainAuthToken):
#     serializer_class = EmailAuthTokenSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                          context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'auth_token': token.key,
#         })
# class CustomAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         # if not serializer.is_valid():
#         #     return Response(
#         #         {'error': 'Неверные учетные данные'},
#         #         status=status.HTTP_400_BAD_REQUEST
#         #     )
#         #serializer.is_valid()
#         username = request.data.get('username')
#         email = request.data.get('email')
#         password = request.data.get('password')
#         print(username)
#         print(email)
#         print(password)
#         if password is None:
#             return Response({
#                 'error': 'Отсутствует пароль'
#             }, status=400)
#         if username is not None:
#             print('Username auth')
#             user = get_object_or_404(User, username=username)
#         elif email is not None:
#             user = get_object_or_404(User, email=email)
#         else:
#             print('None auth')
#             return Response({
#                 'error': 'Отсутствуют данные для аудентификации'
#             }, status=400)
#         #user = serializer.validated_data['user']
#         print('user = ' + user.username)
#         print('user.password = ' + user.password)
#         user_test = User.objects.get({'password': password})
#         print(user_test)
#         if user.password != password:
#             return Response({
#                 'error': 'Неверный пароль'
#             }, status=400)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'auth_token': token.key,
#         })
#
#
# class LoginView(APIView):
#     """
#     View для входа с поддержкой различных комбинаций полей
#     """
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         serializer = MultiFieldAuthSerializer(
#             data=request.data,
#             context={'request': request}
#         )
#
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#
#             # Создание или получение токена
#             token, created = Token.objects.get_or_create(user=user)
#
#             # Сессионная аутентификация (опционально)
#             login(request, user)
#
#             return Response({
#                 'token': token.key,
#                 'user_id': user.pk,
#                 'username': user.username,
#                 'email': user.email,
#                 'message': 'Login successful'
#             }, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
