.PHONY: help install run migrations migrate admin seed shell check docker-dev docker-prod logs

help:
	@echo "install      — зависимости в текущее окружение"
	@echo "migrations   — создать файлы миграций после правки моделей"
	@echo "migrate      — применить миграции"
	@echo "admin        — создать пользователя для панели управления"
	@echo "seed         — заполнить сайт стартовым содержимым"
	@echo "run          — сервер разработки на localhost:8000"
	@echo "check        — проверка проекта перед деплоем"
	@echo "docker-dev   — поднять в Docker для разработки"
	@echo "docker-prod  — поднять боевую сборку"

install:
	pip install -r requirements.txt

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

admin:
	python manage.py createsuperuser

seed:
	python manage.py seed_demo

run:
	python manage.py runserver

shell:
	python manage.py shell

check:
	python manage.py check --deploy --settings=config.settings.prod

docker-dev:
	docker compose up --build

docker-prod:
	docker compose -f docker-compose.prod.yml up -d --build

logs:
	docker compose logs -f web
