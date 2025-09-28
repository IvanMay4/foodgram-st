from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('recipes', views.RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    #path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    #path('auth/token/login/', obtain_auth_token),
    path('users/me/avatar/', views.update_user_avatar),
]
