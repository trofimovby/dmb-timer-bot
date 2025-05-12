#!/bin/bash

# ❗ Укажи путь к Python 3.11, если он отличается
PYTHON311="/opt/homebrew/bin/python3.11"

echo "🔍 Проверка Python версии..."
$PYTHON311 --version || { echo "❌ Python 3.11 не найден. Установи его через 'brew install python@3.11'"; exit 1; }

echo "📁 Создание виртуального окружения..."
$PYTHON311 -m venv venv || { echo "❌ Не удалось создать виртуальное окружение"; exit 1; }

echo "✅ Активация окружения..."
source venv/bin/activate || { echo "❌ Не удалось активировать venv"; exit 1; }

echo "⬆️ Обновление pip, setuptools и wheel..."
pip install --upgrade pip setuptools wheel || exit 1

echo "🛠 Установка aiohttp (3.x)..."
pip install "aiohttp<4.0.0" --only-binary :all: || { echo "❌ Не удалось установить aiohttp"; exit 1; }

echo "📦 Установка aiogram 2.25.2 и dotenv..."
pip install aiogram==2.25.2 python-dotenv || { echo "❌ Не удалось установить aiogram или dotenv"; exit 1; }

echo "📌 Установленные версии:"
python --version
pip show aiohttp | grep Version
pip show aiogram | grep Version

echo "✅ Готово! Окружение настроено и готово к работе."
echo "👉 Не забудь активировать его перед запуском: source venv/bin/activate"


