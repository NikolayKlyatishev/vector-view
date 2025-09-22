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
    from pathlib import Path

    print("🚀 Запуск Vector View...")
    print("   Приложение готово к работе")
    print("   Для подключения к базе данных используйте раздел 'Подключения'")
    print("   URL: http://localhost:5001/connections")
    print()
    print("📁 Файлы конфигурации:")
    print(f"   • Подключения: /tmp/vector-view/connections.json")
    print(f"   • Настройки: /tmp/vector-view/user_settings.json")
    print()


# Create the Flask app
app = create_app()


def main():
    """Main entry point for the application."""
    init_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)


if __name__ == "__main__":
    main()
