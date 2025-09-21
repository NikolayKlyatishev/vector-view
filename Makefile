## Python исполняемые файлы внутри venv
PY=./.venv/bin/python
PIP=./.venv/bin/pip

## Доступные цели
.PHONY: help venv deps web test clean

## Цель по умолчанию — показать справку
.DEFAULT_GOAL := help

help: ## Показать доступные цели и описание
	@printf "\033[1mИспользование:\033[0m make <цель>\n\n"
	@printf "\033[36mДоступные цели:\033[0m\n"
	@awk 'BEGIN {FS = ":.*?## "; tgt="\033[1;33m"; rst="\033[0m"} /^[a-zA-Z0-9_\.%\-]+:.*?## / { printf "  %s%-20s%s %s\n", tgt, $$1, rst, $$2 }' $(MAKEFILE_LIST)

venv: ## Создать виртуальное окружение и обновить pip
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip

deps: venv ## Установить зависимости (chromadb, sentence-transformers, flask)
	$(PIP) install chromadb sentence-transformers flask

web: deps ## Запустить веб-интерфейс (http://localhost:5001)
	$(PY) run_web.py

web-custom: deps ## Запустить веб-интерфейс с кастомными настройками
	@echo "Пример использования:"
	@echo "  CHROMA_DB_PATH=/path/to/chroma make web-custom"
	@echo "  COLLECTION_NAME=my-collection make web-custom"
	@echo "  FLASK_PORT=8080 make web-custom"
	@echo ""
	$(PY) run_web.py

test: deps ## Тестировать веб-интерфейс
	$(PY) test_web.py

clean: ## Удалить виртуальное окружение
	rm -rf .venv

install: deps ## Установить зависимости и подготовить к работе
	@echo "✓ Зависимости установлены"
	@echo "✓ Готово к работе!"
	@echo ""
	@echo "Для запуска веб-интерфейса выполните:"
	@echo "  make web"
	@echo ""
	@echo "Убедитесь, что в родительском каталоге создан индекс:"
	@echo "  cd .. && make index"
