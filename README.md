# Foodgram :bento:

## Описание

Онлайн-сервис Foodgram и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Доступный функционал

- Аутентификация реализована с помощью стандартного модуля DRF - Authtoken.
- У неаутентифицированных пользователей доступ к API только на уровне чтения.
- Создание объектов разрешено только зарегистрированным пользователям.
- Управление пользователями.
- Возможность получения подробной информации о себе и ее редактирование.
- Возможность подписаться на других пользователей и отписаться от них.
- Получение списка всех тегов и ингредиентов.
- Получение списка всех рецептов, их добавление.Получение, обновление и удаление конкретного рецепта.
- Возможность добавить рецепт в избранное.
- Возможность добавить рецепт в список покупок.
- Возможность скачать список покупок в PDF формате.
- Фильтрация по полям.


https://github.com/PUpi-83/foodgram-project-react/assets/120481017/b6dd0cd7-c9bc-42cd-8dce-170fe38e9381


#### Документация к API доступна по адресу <http://localhost/api/docs/> после локального запуска проекта

#### Технологи

- Python 3.9
- Django 3.2.6
- Django Rest Framework 3.12.4
- Authtoken
- Docker
- Docker-compose
- PostgreSQL
- Gunicorn
- Nginx
- GitHub Actions

## Учетная запись администратора:

```bash
- логин: foodkitty32
- почта:nastos@gmail.com
- пароль: TwinKi320211
```

#### Локальный запуск проекта

- Склонировать репозиторий:

```bash
   git clone https://github.com/PUpi-83/foodgram-project-react.git
```

```bash
   cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

Команда для установки виртуального окружения на Mac или Linux:

```bash
   python3 -m venv env
   source env/bin/activate
```

Команда для Windows:

```bash
   python -m venv venv
   source venv/Scripts/activate
```

- Перейти в директорию infra:

```bash
   cd infra
```

- Создать файл .env по образцу:

```bash
   cp .env.example .env
```

- Выполнить команду для доступа к документации:

```bash
   docker-compose up 
```

Установить зависимости из файла requirements.txt:

```bash
   cd ..
   cd backend
   pip install -r requirements.txt
```

```bash
   python manage.py migrate
```

Заполнить базу тестовыми данными об ингредиентах:

```bash
   python manage.py load_ingredients
```

Создать суперпользователя, если необходимо:

```bash
python manage.py createsuperuser
```

- Запустить локальный сервер:

```bash
   python manage.py runserver
```

### Инструкция для разворачивания проекта на удаленном сервере:

- Склонируйте проект из репозитория:

```bash
$ git clone https://github.com/PUpi-83/foodgram-project-react.git
```

- Выполните вход на удаленный сервер

- Установите DOCKER на сервер:
```bash
apt install docker.io 
```

- Установитe docker-compose на сервер:
```bash
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

- Отредактируйте конфигурацию сервера NGNIX:
```bash
Локально измените файл ..infra/nginx.conf - замените данные в строке server_name на IP-адрес удаленного сервера
```

- Скопируйте файлы docker-compose.yml и nginx.conf из директории ../infra/ на удаленный сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yaml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- Создайте переменные окружения (указаны в файле ../infra/.env)

- Установите и активируйте виртуальное окружение (для Windows):

```bash
python -m venv venv 
source venv/Scripts/activate
python -m pip install --upgrade pip
``` 

- Запустите приложение в контейнерах:

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

- Смотрим название контейнера backend:

```bash
sudo docker ps | grep backend
```

- Заходим в контейнер backend:
```bash
sudo docker exec -it foodgram-backend-1 bash
```

- Выполняем в нем миграции и создаем суперюзера:
```bash
python manage.py migrate
```
```bash
python manage.py createsuperuser
```

- Собираем статику и наполняем базу данных ингредиентами:
```bash
python manage.py collectstatic
```
```bash
python manage.py load_ingredients
```
- Дополнительны команды для работы с контенерами:
```bash
docker compose stop — остановит все контейнеры, но оставит сети и volume. Эта команда пригодится, чтобы перезагрузить или обновить приложения.
docker compose down — остановит все контейнеры, удалит их, сети и анонимные volumes. Можно будет начать всё заново.
docker compose logs — просмотр логов запущенных контейнеров.
```

#### Примеры некоторых запросов API

Регистрация пользователя:

```bash
   POST /api/v1/users/
```

Получение данных своей учетной записи:

```bash
   GET /api/v1/users/me/ 
```

Добавление подписки:

```bash
   POST /api/v1/users/id/subscription/
```

Обновление рецепта:
  
```bash
   PATCH /api/v1/recipes/id/
```

Удаление рецепта из избранного:

```bash
   DELETE /api/v1/recipes/id/favorite/
```

Получение списка ингредиентов:

```bash
   GET /api/v1/ingredients/
```

Скачать список покупок:

```bash
   GET /api/v1/recipes/download_shopping_cart/
```

#### Полный список запросов API находятся в [документации](http://localhost/api/docs/)

### Проект можно посмотреть [здесь](https://foodgramkitty.sytes.net/recipes)

## Автор: [Анастасия](https://github.com/PUpi-83):sunflower:
