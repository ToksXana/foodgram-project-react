# Продуктовый помощник.
Сайт расположен по адресу http://tastygram.ddns.net/
логин: admin
пароль: admin

## Описание проекта
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

#### Документацию к API можно найти по адресу:

{host}/api/docs/

#### Примеры работы с API

Для неавторизованных пользователей работа с API доступна в режиме чтения.

##### Доступно без токена:

Список рецептов
Доступна фильтрация по тегам.

{host}/api/recipes/ 'GET'

Получение рецепта

{host}/api/recipes/{id}/ 'GET'

Список пользователей

{host}/api/users/ 'GET'

Профиль пользователя

{host}/api/users/{id}/ 'GET'

Регистрация пользователя

{host}/api/users/ 'POST'

##### Доступно по токену:

Текущий пользователь

{host}/api/users/me/ 'GET'

Создание рецепта

{host}/api/recipes/ 'POST'

Список покупок(Скачать файл со списком покупок.)

{host}/api/recipes/download_shopping_cart/ 'GET'

Добавить рецепт в избранное

{host}/api/recipes/{id}/favorite/ 'POST'

Подписаться на пользователя

{host}/api/users/{id}/subscribe/ 'POST'

Мои подписки

{host}/api/users/subscriptions/ 'GET'

### Запуск проекта

1. Склонировать репозиторий
2. Установить Docker
3. В корне проекта создайте файл .env и пропишите в него свои данные.
Например:
```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```
3. Установка Nginx
На удалённом сервере запустите Nginx:
```
sudo apt install nginx -y
```
```
sudo systemctl start nginx
```
Открыть файл конфигурации веб-сервера sudo nano /etc/nginx/sites-enabled/default и заменить его содержимое следующим кодом:
```
server {
    server_name публичный_ip_вашего_удаленного_сервера;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```
5. Запустите проект через docker-compose:
```
docker compose -f docker-compose.yml up --build -d
```
Выполнить миграции:
```
docker compose exec backend python manage.py migrate
```
Соберите статику и скопируйте ее:
```
docker compose exec backend python manage.py collectstatic --no-input
```


## Технологии

- Python 3.9.10
- Django 4.2.2
- Django REST Framework 3.14.0
- djoser 2.1.0