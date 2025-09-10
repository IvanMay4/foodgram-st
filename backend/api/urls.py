from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'ingredients', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', views.CurrentUserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
    path('users/me/recipes/', views.CurrentUserViewSet.as_view({'get': 'recipes_list'})),
    path('users/me/subscriptions/', views.CurrentUserViewSet.as_view({'get': 'subscriptions'})),
    path('users/me/favorite/', views.CurrentUserViewSet.as_view({'get': 'favorite_recipes'})),
    path('users/me/shopping_cart/', views.CurrentUserViewSet.as_view({'get': 'shopping_cart_recipes'})),

    path('recipes/<int:pk>/favorite/', views.RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'})),
    path('recipes/<int:pk>/shopping_cart/', views.RecipeViewSet.as_view({'post': 'shopping_cart', 'delete': 'shopping_cart'})),
    path('recipes/download_shopping_cart/', views.RecipeViewSet.as_view({'get': 'download_shopping_cart'})),

    # Дополнительные пути для пользователей (подписка)
    path('users/<int:pk>/subscribe/', views.UserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'})),
    #path('recipes/<int:recipe_id>/favorite/', views.add_favorite, name='add_favorite'),
]
