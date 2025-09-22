#!/usr/bin/env python3
"""
Flask веб-интерфейс для RAG системы.
Предоставляет простой интерфейс для просмотра коллекций, чанков и поиска.
"""

from __future__ import annotations

from flask import Flask

from .config import Config
from .database import db_manager
from . import routes  # Import routes to register them


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Register routes
    app.register_blueprint(routes.bp)

    return app


def init_app():
    """Инициализация приложения."""
    # Проверяем конфигурацию
    if not Config.validate_config():
        print("Конфигурация не прошла проверку. Продолжаем с предупреждениями...")

    # Получаем настройки из конфигурации
    db_path = Config.get_chroma_path()
    collection_name = Config.COLLECTION_NAME
    model_name = Config.EMBEDDING_MODEL

    try:
        db_manager.load_chroma_collection(db_path, collection_name)
        db_manager.load_embedding_model(model_name)
        print(f"Приложение инициализировано.")
        print(f"  База данных: {db_path}")
        print(f"  Коллекция: {collection_name}")
        print(f"  Модель: {model_name}")
    except Exception as e:
        print(f"Ошибка инициализации: {e}")


# Create the Flask app
app = create_app()


def main():
    """Main entry point for the application."""
    init_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)


if __name__ == "__main__":
    main()
