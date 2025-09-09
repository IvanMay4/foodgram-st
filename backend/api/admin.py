from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Recipe, Ingredient, RecipeIngredient, Follow, Favorite, ShoppingCart
from .forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'cooking_time', 'get_ingredients', 'count_favorites')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'pub_date')

    def get_ingredients(self, obj):
        return ", ".join([f"{ri.ingredient.name} ({ri.amount} {ri.ingredient.measurement_unit})" for ri in obj.recipe_ingredients.all()])
    get_ingredients.short_description = 'Ингредиенты'

    def count_favorites(self, obj):
        return obj.favorite_recipes.count()
    count_favorites.short_description = 'В избранном'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', 'get_unit')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')

    def get_unit(self, obj):
        return obj.ingredient.measurement_unit
    get_unit.short_description = 'Единица измерения'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user', 'following')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'avatar')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')

    def avatar_display(self, obj):
        if obj.avatar:
            return format_html('<img src="" width="50" height="50" />', obj.avatar.url)
        return "Нет аватара"
    avatar_display.short_description = 'Аватар'

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    readonly_fields = ('date_joined',)
