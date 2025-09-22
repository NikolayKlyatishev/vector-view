#!/usr/bin/env python3
"""
Конфигурация для RAG веб-интерфейса.
"""

import os
from pathlib import Path


class Config:
    """Конфигурация приложения."""

    # Путь к базе данных Chroma (можно переопределить через переменную окружения)
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "../.chroma")

    # Имя коллекции (можно переопределить через переменную окружения)
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "usage-guides")

    # Модель для эмбеддингов (можно переопределить через переменную окружения)
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Настройки Flask
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "5001"))

    @classmethod
    def get_chroma_path(cls) -> Path:
        """Получить путь к базе данных Chroma как Path объект."""
        return Path(cls.CHROMA_DB_PATH)

    @classmethod
    def validate_config(cls) -> bool:
        """Проверить корректность конфигурации."""
        chroma_path = cls.get_chroma_path()
        if not chroma_path.exists():
            print(
                f"Предупреждение: Путь к базе данных Chroma не существует: {chroma_path}"
            )
            print(f"Создайте индекс командой: make index")
            return False
        return True
