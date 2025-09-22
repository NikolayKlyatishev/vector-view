#!/bin/bash
# Скрипт настройки среды разработки с Poetry

set -e

echo "🛠️ Настройка среды разработки Vector View с Poetry..."

# Проверяем наличие Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry не найден. Установите Poetry:"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    echo "  или"
    echo "  pip install poetry"
    exit 1
fi

echo "✅ Poetry найден: $(poetry --version)"

# Устанавливаем зависимости для разработки
echo "📚 Установка зависимостей для разработки..."
poetry install --with dev

# Устанавливаем pre-commit hooks
echo "🔧 Настройка pre-commit hooks..."
if poetry run pre-commit --version &> /dev/null; then
    poetry run pre-commit install
    echo "✅ Pre-commit hooks установлены"
else
    echo "⚠️ Pre-commit не найден в зависимостях. Добавьте его:"
    echo "  poetry add --group dev pre-commit"
fi

# Создаем конфигурационные файлы
echo "📝 Создание конфигурационных файлов..."

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    cat > .env << EOF
# Vector View Configuration
CHROMA_DB_PATH=../.chroma
COLLECTION_NAME=usage-guides
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Flask Configuration
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
EOF
    echo "✅ Создан файл .env"
else
    echo "ℹ️ Файл .env уже существует"
fi

# Создаем .pre-commit-config.yaml если его нет
if [ ! -f .pre-commit-config.yaml ]; then
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
EOF
    echo "✅ Создан файл .pre-commit-config.yaml"
fi

echo ""
echo "✅ Среда разработки настроена!"
echo ""
echo "Доступные команды:"
echo "  make web          - Запустить веб-интерфейс"
echo "  make test         - Запустить тесты"
echo "  make test-cov     - Запустить тесты с покрытием"
echo "  make lint         - Проверить код линтерами"
echo "  make format       - Форматировать код"
echo "  make check        - Проверить код и запустить тесты"
echo "  make shell        - Активировать shell с виртуальным окружением"
echo ""
echo "Для активации виртуального окружения:"
echo "  poetry shell"
echo ""
echo "Для запуска тестов:"
echo "  make test"
echo ""
echo "Для проверки кода:"
echo "  make lint"