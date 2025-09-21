#!/usr/bin/env python3
"""
Скрипт для запуска веб-интерфейса RAG системы.
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from app import app, init_app
from config import Config

if __name__ == '__main__':
    print("Запуск RAG веб-интерфейса...")
    print(f"Конфигурация:")
    print(f"  База данных: {Config.CHROMA_DB_PATH}")
    print(f"  Коллекция: {Config.COLLECTION_NAME}")
    print(f"  Модель: {Config.EMBEDDING_MODEL}")
    print(f"  Хост: {Config.HOST}:{Config.PORT}")
    print()
    print("Убедитесь, что вы запустили 'make index' для создания индекса")
    print("Нажмите Ctrl+C для остановки")
    print()
    
    init_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
