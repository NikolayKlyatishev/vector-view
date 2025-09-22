#!/bin/bash
# Скрипт установки Vector View с Poetry

set -e

echo "🚀 Установка Vector View с Poetry..."

# Проверяем наличие Python 3.9+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.9 или выше."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Требуется Python 3.9 или выше. Найден: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION найден"

# Проверяем наличие Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry не найден. Установите Poetry:"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    echo "  или"
    echo "  pip install poetry"
    exit 1
fi

echo "✅ Poetry найден: $(poetry --version)"

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
poetry install

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Для запуска приложения выполните:"
echo "  make web"
echo ""
echo "Или напрямую:"
echo "  poetry run vector-view"
echo ""
echo "Для активации виртуального окружения:"
echo "  poetry shell"
echo ""
echo "Для настройки переменных окружения создайте файл .env:"
echo "  CHROMA_DB_PATH=/path/to/your/chroma"
echo "  COLLECTION_NAME=your-collection"
echo "  FLASK_PORT=5001"
