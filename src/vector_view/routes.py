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

# Create blueprint
bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Главная страница."""
    return render_template("index.html")


@bp.route("/collections")
def collections():
    """Страница просмотра коллекций."""
    try:
        collections_data = db_manager.get_collections()
        return render_template("collections.html", collections=collections_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/collections")
def api_collections():
    """API для получения списка коллекций."""
    try:
        collections_data = db_manager.get_collections()
        return jsonify(collections_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/chunks")
def chunks():
    """Страница просмотра чанков."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        chunks_data = db_manager.get_chunks(page, per_page)
        return render_template("chunks.html", **chunks_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/chunks")
def api_chunks():
    """API для получения чанков."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        chunks_data = db_manager.get_chunks(page, per_page)
        return jsonify(chunks_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        }
        return jsonify(settings_data)
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
