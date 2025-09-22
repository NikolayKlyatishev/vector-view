"""
Flask routes for Vector View application.

Contains all web routes and API endpoints.
"""

from __future__ import annotations

import os
from importlib import reload

from flask import Blueprint, render_template, request, jsonify

from .config import Config
from .database import db_manager
from .connections import connection_manager
from .user_settings import user_settings

# Create blueprint
bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Главная страница."""
    db_status = db_manager.get_status()
    connection_status = connection_manager.get_status()
    return render_template(
        "index.html", db_status=db_status, connection_status=connection_status
    )


@bp.route("/collections")
def collections():
    """Страница просмотра коллекций."""
    try:
        collections_data = db_manager.get_collections()
        return render_template("collections.html", collections=collections_data)
    except Exception as e:
        return render_template(
            "collections.html",
            collections=[],
            error=str(e),
            db_status=db_manager.get_status(),
        )


@bp.route("/api/collections")
def api_collections():
    """API для получения списка коллекций."""
    try:
        collections_data = db_manager.get_collections()
        return jsonify(collections_data)
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "collections": [],
                    "db_status": db_manager.get_status(),
                }
            ),
            500,
        )


@bp.route("/chunks")
def chunks():
    """Страница просмотра чанков."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        chunks_data = db_manager.get_chunks(page, per_page)
        return render_template("chunks.html", **chunks_data)
    except Exception as e:
        return render_template(
            "chunks.html",
            chunks=[],
            page=1,
            per_page=20,
            total_count=0,
            total_pages=0,
            error=str(e),
            db_status=db_manager.get_status(),
        )


@bp.route("/api/chunks")
def api_chunks():
    """API для получения чанков."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        chunks_data = db_manager.get_chunks(page, per_page)
        return jsonify(chunks_data)
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "chunks": [],
                    "page": 1,
                    "per_page": 20,
                    "total_count": 0,
                    "total_pages": 0,
                    "db_status": db_manager.get_status(),
                }
            ),
            500,
        )


@bp.route("/search")
def search():
    """Страница поиска."""
    return render_template("search.html")


@bp.route("/api/search", methods=["POST"])
def api_search():
    """API для поиска."""
    try:
        data = request.get_json()
        query_text = data.get("query", "")
        schema_filter = data.get("schema_filter")
        top_k = int(data.get("top_k", 5))

        search_results = db_manager.search(query_text, schema_filter, top_k)
        return jsonify(search_results)
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "query": query_text,
                    "schema_filter": schema_filter,
                    "top_k": top_k,
                    "results": [],
                    "db_status": db_manager.get_status(),
                }
            ),
            500,
        )


@bp.route("/vectors")
def vectors():
    """Страница визуализации векторов."""
    return render_template("vectors.html")


@bp.route("/api/vectors")
def api_vectors():
    """API для получения векторов для визуализации."""
    try:
        limit = int(request.args.get("limit", 100))
        schema_filter = request.args.get("schema")

        vectors_data = db_manager.get_vectors(limit, schema_filter)
        return jsonify(vectors_data)
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "vectors": [],
                    "total_count": 0,
                    "schema_filter": schema_filter,
                    "db_status": db_manager.get_status(),
                }
            ),
            500,
        )


@bp.route("/settings")
def settings():
    """Страница настроек."""
    return render_template("settings.html")


@bp.route("/api/settings")
def api_get_settings():
    """API для получения текущих настроек."""
    try:
        settings_data = {
            "chroma_db_path": Config.CHROMA_DB_PATH,
            "collection_name": Config.COLLECTION_NAME,
            "embedding_model": Config.EMBEDDING_MODEL,
            "flask_debug": Config.DEBUG,
            "flask_host": Config.HOST,
            "flask_port": Config.PORT,
            "db_status": db_manager.get_status(),
        }
        return jsonify(settings_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/db-status")
def api_db_status():
    """API для получения статуса базы данных."""
    try:
        status = db_manager.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/settings", methods=["POST"])
def api_update_settings():
    """API для обновления настроек."""
    try:
        data = request.get_json()

        # Update environment variables
        if "chroma_db_path" in data:
            os.environ["CHROMA_DB_PATH"] = data["chroma_db_path"]
        if "collection_name" in data:
            os.environ["COLLECTION_NAME"] = data["collection_name"]
        if "embedding_model" in data:
            os.environ["EMBEDDING_MODEL"] = data["embedding_model"]
        if "flask_debug" in data:
            os.environ["FLASK_DEBUG"] = str(data["flask_debug"]).lower()
        if "flask_host" in data:
            os.environ["FLASK_HOST"] = data["flask_host"]
        if "flask_port" in data:
            os.environ["FLASK_PORT"] = str(data["flask_port"])

        # Reload configuration
        import config

        reload(config)
        Config = config.Config

        return jsonify({"message": "Настройки обновлены", "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@bp.route("/api/validate-folder", methods=["POST"])
def api_validate_folder():
    """API для валидации папки с базой данных Chroma."""
    try:
        data = request.get_json()
        folder_path = data.get("folder_path", "")

        validation_result = db_manager.validate_chroma_folder(folder_path)
        return jsonify(validation_result)
    except Exception as e:
        return jsonify({"valid": False, "message": f"Ошибка валидации: {str(e)}"}), 500


# Connection Management Routes
@bp.route("/connections")
def connections():
    """Страница управления подключениями."""
    return render_template("connections.html")


@bp.route("/api/connections")
def api_get_connections():
    """API для получения списка подключений."""
    try:
        connections = connection_manager.list_connections()
        status = connection_manager.get_status()
        return jsonify(
            {"connections": [conn.to_dict() for conn in connections], "status": status}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections", methods=["POST"])
def api_create_connection():
    """API для создания нового подключения."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "db_path", "collection_name", "embedding_model"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Поле '{field}' обязательно"}), 400

        # Create connection config
        from .connections import ConnectionConfig
        import uuid

        conn_config = ConnectionConfig(
            id=str(uuid.uuid4()),
            name=data["name"],
            db_path=data["db_path"],
            collection_name=data["collection_name"],
            embedding_model=data["embedding_model"],
            description=data.get("description", ""),
        )

        # Validate connection
        validation = connection_manager.validate_connection(
            conn_config.db_path, conn_config.collection_name
        )

        if not validation["valid"]:
            return jsonify({"error": validation["message"]}), 400

        # Add connection
        conn_id = connection_manager.add_connection(conn_config)

        return jsonify(
            {
                "success": True,
                "connection_id": conn_id,
                "connection": conn_config.to_dict(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections/<conn_id>", methods=["PUT"])
def api_update_connection(conn_id):
    """API для обновления подключения."""
    try:
        data = request.get_json()

        # Get existing connection
        existing_conn = connection_manager.get_connection(conn_id)
        if not existing_conn:
            return jsonify({"error": "Подключение не найдено"}), 404

        # Update fields
        for field in [
            "name",
            "db_path",
            "collection_name",
            "embedding_model",
            "description",
        ]:
            if field in data:
                setattr(existing_conn, field, data[field])

        # Validate connection if path or collection changed
        if "db_path" in data or "collection_name" in data:
            validation = connection_manager.validate_connection(
                existing_conn.db_path, existing_conn.collection_name
            )

            if not validation["valid"]:
                return jsonify({"error": validation["message"]}), 400

        # Update connection
        success = connection_manager.update_connection(conn_id, existing_conn)

        if not success:
            return jsonify({"error": "Ошибка обновления подключения"}), 500

        return jsonify({"success": True, "connection": existing_conn.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections/<conn_id>", methods=["DELETE"])
def api_delete_connection(conn_id):
    """API для удаления подключения."""
    try:
        success = connection_manager.delete_connection(conn_id)

        if not success:
            return jsonify({"error": "Подключение не найдено"}), 404

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections/<conn_id>/connect", methods=["POST"])
def api_connect(conn_id):
    """API для подключения к базе данных."""
    try:
        success = connection_manager.connect(conn_id)

        if not success:
            return jsonify({"error": "Ошибка подключения"}), 500

        return jsonify(
            {
                "success": True,
                "connection": connection_manager.get_active_connection().to_dict(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections/disconnect", methods=["POST"])
def api_disconnect():
    """API для отключения от базы данных."""
    try:
        connection_manager.disconnect()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections/validate", methods=["POST"])
def api_validate_connection():
    """API для валидации подключения."""
    try:
        data = request.get_json()
        db_path = data.get("db_path", "")
        collection_name = data.get("collection_name", "")

        validation = connection_manager.validate_connection(db_path, collection_name)
        return jsonify(validation)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/user-settings/recent-paths", methods=["GET"])
def api_get_recent_paths():
    """API для получения недавних путей."""
    try:
        recent_paths = user_settings.get_recent_paths()
        return jsonify({"recent_paths": recent_paths})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/user-settings/last-used", methods=["GET"])
def api_get_last_used():
    """API для получения последних использованных настроек."""
    try:
        return jsonify(
            {
                "last_db_path": user_settings.get_last_db_path(),
                "last_collection": user_settings.get_last_collection(),
                "last_model": user_settings.get_last_model(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/user-settings/save", methods=["POST"])
def api_save_user_settings():
    """API для сохранения настроек пользователя."""
    try:
        data = request.get_json()

        if "last_db_path" in data:
            user_settings.set_last_db_path(data["last_db_path"])
        if "last_collection" in data:
            user_settings.set_last_collection(data["last_collection"])
        if "last_model" in data:
            user_settings.set_last_model(data["last_model"])

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/user-settings/resolve-path", methods=["POST"])
def api_resolve_path():
    """API для разрешения пути к выбранной папке."""
    try:
        data = request.get_json()
        folder_name = data.get("folder_name", "")

        # For now, we'll return the folder name as the path
        # In a real implementation, you might want to:
        # 1. Search for the folder in common locations
        # 2. Use the current working directory
        # 3. Ask the user to provide the full path

        # Try to find the folder in common locations
        import os
        from pathlib import Path

        common_paths = [
            os.getcwd(),  # Current working directory
            os.path.expanduser("~"),  # Home directory
            os.path.expanduser("~/Documents"),  # Documents folder
            os.path.expanduser("~/Desktop"),  # Desktop folder
        ]

        full_path = None
        for base_path in common_paths:
            potential_path = Path(base_path) / folder_name
            if potential_path.exists() and potential_path.is_dir():
                full_path = str(potential_path.absolute())
                break

        if full_path:
            return jsonify(
                {
                    "success": True,
                    "full_path": full_path,
                    "message": f"Найдена папка: {full_path}",
                }
            )
        else:
            # Return the folder name as is, user can modify it manually
            return jsonify(
                {
                    "success": True,
                    "full_path": folder_name,
                    "message": f"Папка не найдена в стандартных местах. Проверьте путь: {folder_name}",
                }
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/connections/create-collection", methods=["POST"])
def api_create_collection():
    """API для создания новой коллекции."""
    try:
        data = request.get_json()
        db_path = data.get("db_path", "")
        collection_name = data.get("collection_name", "")
        embedding_model = data.get(
            "embedding_model",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )

        if not db_path or not collection_name:
            return jsonify({"error": "Путь к БД и имя коллекции обязательны"}), 400

        # Validate the path first
        validation = connection_manager.validate_connection(db_path, "")
        if not validation["valid"]:
            return jsonify({"error": validation["message"]}), 400

        # Create the collection
        import chromadb
        from pathlib import Path

        client = chromadb.PersistentClient(path=str(Path(db_path).absolute()))

        # Check if collection already exists
        existing_collections = client.list_collections()
        if any(col.name == collection_name for col in existing_collections):
            return (
                jsonify({"error": f"Коллекция '{collection_name}' уже существует"}),
                400,
            )

        # Create new collection
        collection = client.create_collection(
            name=collection_name,
            embedding_function=None,  # Will use default embedding function
        )

        return jsonify(
            {
                "success": True,
                "message": f"Коллекция '{collection_name}' создана успешно",
                "collection": {"name": collection.name, "id": collection.id},
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
