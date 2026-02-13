# Указываем базовый образ
FROM python:3.12-slim

# предотвращает создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1

# отключает буферизацию stdout и stderr потоков
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .

# Копируем остальные файлы проекта в контейнер
COPY . .

# Открываем порт 8000 для взаимодействия с приложением
EXPOSE 8000

# Определяем команду для запуска приложения
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]