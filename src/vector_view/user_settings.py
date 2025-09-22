#!/usr/bin/env python3
"""
Управление настройками пользователя.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class UserSettings:
    """Класс для управления настройками пользователя."""

    def __init__(self, settings_file: str = None):
        """Инициализация с файлом настроек."""
        if settings_file is None:
            # Create /tmp/vector-view directory if it doesn't exist
            tmp_dir = Path("/tmp/vector-view")
            tmp_dir.mkdir(exist_ok=True)
            settings_file = str(tmp_dir / "user_settings.json")

        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Загрузить настройки из файла."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки настроек: {e}")
                return self._get_default_settings()
        return self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Получить настройки по умолчанию."""
        return {
            "last_db_path": "",
            "last_collection": "",
            "last_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "recent_paths": [],
            "preferences": {"auto_connect": False, "remember_path": True},
        }

    def _save_settings(self) -> None:
        """Сохранить настройки в файл."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения настроек: {e}")

    def get_last_db_path(self) -> str:
        """Получить последний использованный путь к БД."""
        return self.settings.get("last_db_path", "")

    def set_last_db_path(self, path: str) -> None:
        """Установить последний использованный путь к БД."""
        self.settings["last_db_path"] = path

        # Добавить в список недавних путей
        recent_paths = self.settings.get("recent_paths", [])
        if path in recent_paths:
            recent_paths.remove(path)
        recent_paths.insert(0, path)

        # Ограничить количество недавних путей
        self.settings["recent_paths"] = recent_paths[:10]

        self._save_settings()

    def get_recent_paths(self) -> list:
        """Получить список недавних путей."""
        return self.settings.get("recent_paths", [])

    def get_last_collection(self) -> str:
        """Получить последнюю использованную коллекцию."""
        return self.settings.get("last_collection", "")

    def set_last_collection(self, collection: str) -> None:
        """Установить последнюю использованную коллекцию."""
        self.settings["last_collection"] = collection
        self._save_settings()

    def get_last_model(self) -> str:
        """Получить последнюю использованную модель."""
        return self.settings.get(
            "last_model", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def set_last_model(self, model: str) -> None:
        """Установить последнюю использованную модель."""
        self.settings["last_model"] = model
        self._save_settings()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Получить настройку пользователя."""
        return self.settings.get("preferences", {}).get(key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """Установить настройку пользователя."""
        if "preferences" not in self.settings:
            self.settings["preferences"] = {}
        self.settings["preferences"][key] = value
        self._save_settings()

    def get_all_settings(self) -> Dict[str, Any]:
        """Получить все настройки."""
        return self.settings.copy()

    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """Обновить настройки."""
        self.settings.update(new_settings)
        self._save_settings()


# Глобальный экземпляр настроек
user_settings = UserSettings()
