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
ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0
DEBUG=False
```

Запустить docker compose:
```bash
docker-compose up -d --build
```

Запустить сервер для работы с реальными пользователями (включается оформление на сайте)
```bash
docker-compose exec -d backend python manage.py runserver
```

Запустить сервер для отладки (например тесты Postman):
```bash
python backend/manage.py migrate
python backend/manage.py load_ingredients
python backend/manage.py runserver 0.0.0.0:8001
# 0.0.0.0:8001 для того, чтобы не было конфликтов нескольких runserver
```