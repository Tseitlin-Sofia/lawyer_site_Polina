FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data \
    MEDIA_ROOT=/app/media

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Postgres-драйвер ставится здесь заранее: контейнер один и тот же
# для SQLite и для Postgres, переключение — через DATABASE_URL.
COPY requirements.txt requirements-postgres.txt ./
RUN pip install --upgrade pip && pip install -r requirements-postgres.txt

COPY . .

RUN mkdir -p /app/data /app/media /app/staticfiles \
 && adduser --disabled-password --gecos "" appuser \
 && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
