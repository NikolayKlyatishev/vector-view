## Poetry команды
POETRY = poetry

## Доступные цели
.PHONY: help install dev web test clean build dist lint format docker-build docker-run docker-stop docker-clean

## Цель по умолчанию — показать справку
.DEFAULT_GOAL := help

help: ## Показать доступные цели и описание
	@printf "\033[1mИспользование:\033[0m make <цель>\n\n"
	@printf "\033[36mДоступные цели:\033[0m\n"
	@awk 'BEGIN {FS = ":.*?## "; tgt="\033[1;33m"; rst="\033[0m"} /^[a-zA-Z0-9_\.%\-]+:.*?## / { printf "  %s%-20s%s %s\n", tgt, $$1, rst, $$2 }' $(MAKEFILE_LIST)

install: ## Установить зависимости
	$(POETRY) install

dev: ## Установить зависимости для разработки
	$(POETRY) install --with dev

web: install ## Запустить веб-интерфейс (http://localhost:5001)
	$(POETRY) run vector-view

web-custom: install ## Запустить веб-интерфейс с кастомными настройками
	@echo "Пример использования:"
	@echo "  CHROMA_DB_PATH=/path/to/chroma make web-custom"
	@echo "  COLLECTION_NAME=my-collection make web-custom"
	@echo "  FLASK_PORT=8080 make web-custom"
	@echo ""
	$(POETRY) run vector-view

test: install ## Тестировать веб-интерфейс
	$(POETRY) run pytest

test-cov: install ## Запустить тесты с покрытием
	$(POETRY) run pytest --cov=src/vector_view --cov-report=html --cov-report=term-missing

lint: install ## Проверить код
	$(POETRY) run black --check src/ tests/

format: install ## Форматировать код
	$(POETRY) run black src/ tests/

build: install ## Собрать пакет
	$(POETRY) build

dist: build ## Создать дистрибутив
	@echo "✓ Дистрибутив создан в dist/"

publish: build ## Опубликовать пакет в PyPI
	$(POETRY) publish

check: lint test ## Проверить код и запустить тесты

clean: ## Удалить временные файлы и кэш Poetry
	$(POETRY) cache clear --all pypi
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

clean-all: clean ## Полная очистка включая .chroma и виртуальное окружение
	$(POETRY) env remove --all
	rm -rf .chroma/

env-info: ## Показать информацию о виртуальном окружении
	$(POETRY) env info

shell: install ## Активировать shell с виртуальным окружением
	$(POETRY) shell

# Docker команды
docker-build: ## Собрать Docker образ
	docker build -t vector-view .

docker-run: docker-build ## Запустить контейнер
	docker-compose up -d

docker-dev: docker-build ## Запустить контейнер в режиме разработки
	docker-compose --profile dev up -d vector-view-dev

docker-stop: ## Остановить контейнер
	docker-compose down

docker-clean: docker-stop ## Очистить Docker образы и контейнеры
	docker rmi vector-view || true
	docker system prune -f
