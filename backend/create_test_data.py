import os
import django
from django.contrib.auth import get_user_model
from api.models import Recipe, Ingredient, Tag, RecipeIngredient
from api.models import Subscribe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


User = get_user_model()


def create_test_data():
    # Проверяем и создаем пользователей только если они не существуют
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'user1@example.com',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password': 'password123'
        }
    )
    if created:
        user1.set_password('password123')
        user1.save()
        print(f"Создан пользователь: {user1.username}")
    else:
        print(f"Пользователь {user1.username} уже существует")

    user2, created = User.objects.get_or_create(
        username='testuser2',
        defaults={
            'email': 'user2@example.com',
            'first_name': 'Мария',
            'last_name': 'Петрова',
            'password': 'password123'
        }
    )
    if created:
        user2.set_password('password123')
        user2.save()
        print(f"Создан пользователь: {user2.username}")
    else:
        print(f"Пользователь {user2.username} уже существует")

    # Создаем теги
    breakfast_tag, created = Tag.objects.get_or_create(
        name='Завтрак',
        defaults={
            'color': '#FF5733',
            'slug': 'breakfast'
        }
    )
    if created:
        print(f"Создан тег: {breakfast_tag.name}")

    lunch_tag, created = Tag.objects.get_or_create(
        name='Обед',
        defaults={
            'color': '#33FF57',
            'slug': 'lunch'
        }
    )
    if created:
        print(f"Создан тег: {lunch_tag.name}")

    # Создаем рецепты
    recipe1, created = Recipe.objects.get_or_create(
        name='Омлет с сыром',
        defaults={
            'author': user1,
            'text': 'Взбить яйца, добавить сыр, жарить на сковороде',
            'cooking_time': 15,
        }
    )
    if created:
        recipe1.tags.add(breakfast_tag)
        print(f"Создан рецепт: {recipe1.name}")

    recipe2, created = Recipe.objects.get_or_create(
        name='Салат овощной',
        defaults={
            'author': user2,
            'text': 'Нарезать овощи, заправить маслом',
            'cooking_time': 20,
        }
    )
    if created:
        recipe2.tags.add(lunch_tag)
        print(f"Создан рецепт: {recipe2.name}")

    # Добавляем ингредиенты к рецептам
    try:
        egg = Ingredient.objects.get(name='Яйцо')
        cheese = Ingredient.objects.get(name='Сыр')
        tomato = Ingredient.objects.get(name='Помидор')
        cucumber = Ingredient.objects.get(name='Огурец')

        # Для рецепта 1
        if created:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe1,
                ingredient=egg,
                defaults={'amount': 3}
            )
            RecipeIngredient.objects.get_or_create(
                recipe=recipe1,
                ingredient=cheese,
                defaults={'amount': 100}
            )
            print("Добавлены ингредиенты к омлету")

        # Для рецепта 2
        if created:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe2,
                ingredient=tomato,
                defaults={'amount': 2}
            )
            RecipeIngredient.objects.get_or_create(
                recipe=recipe2,
                ingredient=cucumber,
                defaults={'amount': 1}
            )
            print("Добавлены ингредиенты к салату")

    except Ingredient.DoesNotExist:
        print("Некоторые ингредиенты не найдены в базе данных")
        print("Сначала выполните: python backend/manage.py load_ingredients")

    # Создаем подписку
    subscribe, created = Subscribe.objects.get_or_create(
        user=user1,
        author=user2
    )
    if created:
        print(f"Создана подписка: {user1.username} -> {user2.username}")

    print("Тестовые данные созданы/проверены успешно!")


if __name__ == '__main__':
    create_test_data()
