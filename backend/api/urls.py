from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

#router.register(r'users', views.UserViewSet, basename='user')
#router.register(r'recipes', views.RecipeViewSet, basename='recipe')
#router.register(r'ingredients', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    #path('', include(router.urls)),
    #path('users/<int:user_id>/subscribe/', views.subscribe_user, name='subscribe_user'),
    #path('recipes/<int:recipe_id>/favorite/', views.add_favorite, name='add_favorite'),
]