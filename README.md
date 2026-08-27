# Сайт юриста по трудовому праву

Django-проект: услуги с ценами, блок об опыте, панель управления для владелицы
сайта и главное — кнопки с готовыми вопросами, которые превращаются в заявку
за два клика. Уведомление приходит в Telegram, статус заявки отмечается в панели.

---

## 1. Первый запуск на своей машине

```bash
cd lawyer_site

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Сгенерируйте ключ и впишите его в `.env` в поле `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Дальше — миграции и запуск:

```bash
python manage.py makemigrations core services leads
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Сайт: http://127.0.0.1:8000
Панель управления: http://127.0.0.1:8000/admin/

`seed_demo` кладёт стартовые услуги, цены и десяток вопросов по трудовому
праву. Всё это правится в панели — трогать код не нужно.

---

## 2. То же самое в Docker

```bash
cp .env.example .env                       # ключ впишите так же
docker compose up --build

# в другом терминале, один раз:
docker compose exec web python manage.py makemigrations core services leads
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo
```

Код примонтирован с хоста, сервер перезапускается сам при правке файлов.

---

## 3. Telegram-уведомления

1. В Telegram напишите `@BotFather` → `/newbot` → получите токен.
2. Сестра пишет своему боту любое сообщение (иначе бот не сможет ей писать).
3. Узнайте `chat_id`: откройте
   `https://api.telegram.org/bot<ТОКЕН>/getUpdates` и найдите `"chat":{"id":...}`.
4. В `.env`:

```
NOTIFICATION_BACKENDS=telegram
TELEGRAM_BOT_TOKEN=123456:AA...
TELEGRAM_CHAT_ID=987654321
SITE_URL=https://ваш-домен
```

Несколько каналов сразу — через запятую: `telegram,email`.
Проверка без реальной отправки: `NOTIFICATION_BACKENDS=console` — текст
уведомления просто печатается в логи.

---

## 4. Что где лежит

```
config/settings/   base.py — общее, dev.py — разработка, prod.py — боевые настройки
apps/common/       абстрактные модели: даты, порядок сортировки, singleton
apps/core/         настройки сайта, опыт, образование, страницы
apps/services/     направления, услуги, цены
apps/leads/        готовые вопросы и заявки
apps/notifications/каналы доставки: telegram, email, console
templates/         шаблоны, includes/_questions.html — те самые кнопки
static/            css и js
```

Точки расширения:

- **новый канал уведомлений** — класс в `apps/notifications/backends.py`
  и строка в словаре `BACKENDS`;
- **фоновая отправка** — `apps/leads/signals.py` заменить на постановку задачи
  в очередь, остальной код не меняется;
- **Postgres вместо SQLite** — одна переменная `DATABASE_URL`;
- **второй язык** — `LANGUAGES` в `base.py`, i18n уже включён.

---

## 5. Деплой

### Вариант А: свой сервер (Hetzner ~4 €/мес, Oracle Cloud free tier)

```bash
ssh user@сервер
git clone <репозиторий> && cd lawyer_site

cp .env.example .env && nano .env
# DEBUG=0
# SECRET_KEY=<длинный случайный>
# ALLOWED_HOSTS=ваш-домен.com
# CSRF_TRUSTED_ORIGINS=https://ваш-домен.com
# SITE_URL=https://ваш-домен.com
# DOMAIN=ваш-домен.com
# NOTIFICATION_BACKENDS=telegram + токен и chat_id

docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.prod.yml exec web python manage.py seed_demo
```

A-запись домена должна указывать на IP сервера — Caddy сам получит сертификат.

### Вариант Б: PaaS (Fly.io, Koyeb, Railway)

Берут `Dockerfile` как есть. Обязательно:

- переменные окружения из `.env` перенести в настройки платформы;
- подключить постоянный диск и смонтировать его в `/app/data`
  (иначе SQLite-база исчезнет при перезапуске);
- `DJANGO_SETTINGS_MODULE=config.settings.prod`.

Перед выкладкой:

```bash
python manage.py check --deploy --settings=config.settings.prod
```

---

## 6. Регулярные команды

```bash
make migrations   # после любой правки моделей
make migrate
make seed
make run
make check        # проверка боевых настроек
make docker-prod
```

## 7. Резервная копия

```bash
docker compose -f docker-compose.prod.yml exec web \
  python manage.py dumpdata --indent 2 \
  core services leads > backup-$(date +%F).json
```

Восстановление: `python manage.py loaddata backup-2026-01-01.json`
