"""
Connection management module for Vector View.

Handles multiple ChromaDB connections and switching between them.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer


@dataclass
class ConnectionConfig:
    """Configuration for a database connection."""

    id: str
    name: str
    db_path: str
    collection_name: str
    embedding_model: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    is_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConnectionConfig":
        """Create from dictionary."""
        return cls(**data)


class ConnectionManager:
    """Manages multiple database connections."""

    def __init__(self, config_file: str = None):
        if config_file is None:
            # Create /tmp/vector-view directory if it doesn't exist
            tmp_dir = Path("/tmp/vector-view")
            tmp_dir.mkdir(exist_ok=True)
            config_file = str(tmp_dir / "connections.json")

        self.config_file = Path(config_file)
        self.connections: Dict[str, ConnectionConfig] = {}
        self.active_connection_id: Optional[str] = None
        self.current_client: Optional[chromadb.PersistentClient] = None
        self.current_collection = None
        self.current_model: Optional[SentenceTransformer] = None

        self.load_connections()

    def load_connections(self) -> None:
        """Load connections from config file."""
        if not self.config_file.exists():
            self.connections = {}
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for conn_id, conn_data in data.get("connections", {}).items():
                self.connections[conn_id] = ConnectionConfig.from_dict(conn_data)

            self.active_connection_id = data.get("active_connection_id")

        except Exception as e:
            print(f"Ошибка загрузки подключений: {e}")
            self.connections = {}

    def save_connections(self) -> None:
        """Save connections to config file."""
        try:
            data = {
                "connections": {
                    conn_id: conn.to_dict()
                    for conn_id, conn in self.connections.items()
                },
                "active_connection_id": self.active_connection_id,
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Ошибка сохранения подключений: {e}")

    def add_connection(self, config: ConnectionConfig) -> str:
        """Add a new connection."""
        if not config.created_at:
            config.created_at = datetime.now().isoformat()

        self.connections[config.id] = config
        self.save_connections()
        return config.id

    def update_connection(self, conn_id: str, config: ConnectionConfig) -> bool:
        """Update an existing connection."""
        if conn_id not in self.connections:
            return False

        self.connections[conn_id] = config
        self.save_connections()
        return True

    def delete_connection(self, conn_id: str) -> bool:
        """Delete a connection."""
        if conn_id not in self.connections:
            return False

        # If deleting active connection, clear it
        if self.active_connection_id == conn_id:
            self.disconnect()

        del self.connections[conn_id]
        self.save_connections()
        return True

    def get_connection(self, conn_id: str) -> Optional[ConnectionConfig]:
        """Get connection by ID."""
        return self.connections.get(conn_id)

    def list_connections(self) -> List[ConnectionConfig]:
        """Get list of all connections."""
        return list(self.connections.values())

    def connect(self, conn_id: str) -> bool:
        """Connect to a specific database."""
        if conn_id not in self.connections:
            return False

        config = self.connections[conn_id]

        try:
            # Disconnect from current connection
            self.disconnect()

            # Connect to new database
            self.current_client = chromadb.PersistentClient(path=config.db_path)
            self.current_collection = self.current_client.get_collection(
                config.collection_name
            )
            self.current_model = SentenceTransformer(config.embedding_model)

            # Update active connection
            self.active_connection_id = conn_id
            config.is_active = True
            config.last_used = datetime.now().isoformat()

            # Update other connections
            for other_conn in self.connections.values():
                if other_conn.id != conn_id:
                    other_conn.is_active = False

            self.save_connections()
            return True

        except Exception as e:
            print(f"Ошибка подключения к {config.name}: {e}")
            self.disconnect()
            return False

    def disconnect(self) -> None:
        """Disconnect from current database."""
        self.current_client = None
        self.current_collection = None
        self.current_model = None

        # Update active connection status
        if self.active_connection_id:
            active_conn = self.connections.get(self.active_connection_id)
            if active_conn:
                active_conn.is_active = False

        self.active_connection_id = None
        self.save_connections()

    def is_connected(self) -> bool:
        """Check if currently connected to a database."""
        return (
            self.current_client is not None
            and self.current_collection is not None
            and self.current_model is not None
        )

    def get_active_connection(self) -> Optional[ConnectionConfig]:
        """Get currently active connection."""
        if not self.active_connection_id:
            return None
        return self.connections.get(self.active_connection_id)

    def get_status(self) -> Dict[str, Any]:
        """Get connection manager status."""
        active_conn = self.get_active_connection()

        return {
            "is_connected": self.is_connected(),
            "active_connection_id": self.active_connection_id,
            "active_connection": active_conn.to_dict() if active_conn else None,
            "total_connections": len(self.connections),
            "connections": [conn.to_dict() for conn in self.connections.values()],
        }

    def _resolve_path(self, path: str) -> Optional[str]:
        """Try to resolve a path by searching common locations."""
        import os
        from pathlib import Path

        # If path is already absolute, return it
        if Path(path).is_absolute():
            return path if Path(path).exists() else None

        # Search in common locations
        common_paths = [
            os.getcwd(),  # Current working directory
            os.path.expanduser("~"),  # Home directory
            os.path.expanduser("~/Documents"),  # Documents folder
            os.path.expanduser("~/Desktop"),  # Desktop folder
            os.path.expanduser("~/Downloads"),  # Downloads folder
        ]

        for base_path in common_paths:
            potential_path = Path(base_path) / path
            if potential_path.exists() and potential_path.is_dir():
                return str(potential_path.absolute())

        return None

    def validate_connection(self, db_path: str, collection_name: str) -> Dict[str, Any]:
        """Validate a connection without connecting."""
        if not db_path:
            return {"valid": False, "message": "Путь к базе данных не указан"}

        # Try to resolve the path if it doesn't exist
        db_path_obj = Path(db_path)
        if not db_path_obj.exists():
            # Try to resolve the path by searching common locations
            resolved_path = self._resolve_path(db_path)
            if resolved_path:
                db_path_obj = Path(resolved_path)
            else:
                return {
                    "valid": False,
                    "message": f"Путь к базе данных не существует: {db_path}",
                    "suggestion": "Проверьте правильность пути или используйте кнопку 'Выбрать папку' для выбора существующей папки.",
                }

        if not db_path_obj.is_dir():
            return {"valid": False, "message": "Указанный путь не является папкой"}

        try:
            # Try to connect to Chroma
            temp_client = chromadb.PersistentClient(path=str(db_path_obj))
            collections = temp_client.list_collections()

            # Check if collection exists (only if collection_name is specified)
            collection_exists = True
            if collection_name:
                collection_exists = any(
                    col.name == collection_name for col in collections
                )

            # Get more detailed info about the database
            db_info = {
                "path": str(db_path_obj.absolute()),
                "exists": db_path_obj.exists(),
                "is_dir": db_path_obj.is_dir(),
                "files": (
                    [str(f) for f in db_path_obj.iterdir()]
                    if db_path_obj.exists()
                    else []
                ),
            }

            return {
                "valid": True,
                "message": "Подключение валидно",
                "collections_count": len(collections),
                "collections": [
                    {"name": col.name, "id": col.id} for col in collections
                ],
                "collection_exists": collection_exists,
                "target_collection": collection_name,
                "db_info": db_info,
                "debug_info": {
                    "chroma_version": chromadb.__version__,
                    "client_type": "PersistentClient",
                },
            }

        except PermissionError as e:
            return {
                "valid": False,
                "message": f"Нет прав доступа к папке: {str(e)}. Проверьте права доступа к папке.",
                "suggestion": "Попробуйте выбрать папку в другом месте или предоставьте права доступа.",
            }
        except Exception as e:
            error_msg = str(e)
            if "Operation not permitted" in error_msg:
                return {
                    "valid": False,
                    "message": f"Нет прав доступа к папке: {error_msg}",
                    "suggestion": "Попробуйте выбрать папку в другом месте (например, в папке проекта) или предоставьте права доступа.",
                }
            else:
                return {
                    "valid": False,
                    "message": f"Ошибка подключения к базе данных: {error_msg}",
                }


# Global connection manager instance
connection_manager = ConnectionManager()
