# Foodgram

## Описание проекта

«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

## Запуск проекта

Создать файл `.env` в корневой директории проекта, например:
```env
POSTGRES_USER=django
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY=django-insecure-uuhb&gv1o^h%5w)&8=(0_*3(3a@3_#m9vr%n+rsxu=8(3zt^d&
DEBUG=False
```

Запустить docker compose:
```bash
docker compose up --build
```

Выполнить миграции внутри БД:
```bash
docker compose exec backend python manage.py migrate
```

Загрузить в базу ингредиенты:
```bash
docker compose exec backend python manage.py load_ingredients
```