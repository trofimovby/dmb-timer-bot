# Базовый образ
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное
COPY . .

# Устанавливаем переменные окружения (опционально)
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "bot/main.py"]
