#!/usr/bin/env python3
"""
Flask веб-интерфейс для RAG системы.
Предоставляет простой интерфейс для просмотра коллекций, чанков и поиска.
"""

from __future__ import annotations

import os
from pathlib import Path

import chromadb
from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer

from config import Config

app = Flask(__name__)

# Глобальные переменные для коллекции и модели
collection = None
model = None
client = None


def load_chroma_collection(db_path: Path, collection_name: str):
    """Загрузить коллекцию Chroma из постоянного хранилища."""
    global client
    client = chromadb.PersistentClient(path=str(db_path))
    try:
        return client.get_collection(collection_name)
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки коллекции '{collection_name}': {e}") from e


def load_embedding_model(model_name: str):
    """Загрузить модель sentence transformer."""
    try:
        return SentenceTransformer(model_name)
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки модели '{model_name}': {e}") from e


def init_app():
    """Инициализация приложения."""
    global collection, model
    
    # Проверяем конфигурацию
    if not Config.validate_config():
        print("Конфигурация не прошла проверку. Продолжаем с предупреждениями...")
    
    # Получаем настройки из конфигурации
    db_path = Config.get_chroma_path()
    collection_name = Config.COLLECTION_NAME
    model_name = Config.EMBEDDING_MODEL
    
    try:
        collection = load_chroma_collection(db_path, collection_name)
        model = load_embedding_model(model_name)
        print(f"Приложение инициализировано.")
        print(f"  База данных: {db_path}")
        print(f"  Коллекция: {collection_name}")
        print(f"  Модель: {model_name}")
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
        collection = None
        model = None


@app.route('/')
def index():
    """Главная страница."""
    return render_template('index.html')


@app.route('/collections')
def collections():
    """Страница просмотра коллекций."""
    if not client:
        return jsonify({"error": "Chroma клиент не инициализирован"}), 500
    
    try:
        collections_list = client.list_collections()
        collections_data = []
        
        for col in collections_list:
            col_data = {
                "name": col.name,
                "id": col.id,
                "metadata": col.metadata or {}
            }
            try:
                # Получаем количество документов
                count = col.count()
                col_data["document_count"] = count
            except:
                col_data["document_count"] = "Неизвестно"
            
            collections_data.append(col_data)
        
        return render_template('collections.html', collections=collections_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/collections')
def api_collections():
    """API для получения списка коллекций."""
    if not client:
        return jsonify({"error": "Chroma клиент не инициализирован"}), 500
    
    try:
        collections_list = client.list_collections()
        collections_data = []
        
        for col in collections_list:
            col_data = {
                "name": col.name,
                "id": col.id,
                "metadata": col.metadata or {}
            }
            try:
                count = col.count()
                col_data["document_count"] = count
            except:
                col_data["document_count"] = "Неизвестно"
            
            collections_data.append(col_data)
        
        return jsonify(collections_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chunks')
def chunks():
    """Страница просмотра чанков."""
    if not collection:
        return jsonify({"error": "Коллекция не загружена"}), 500
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Получаем все документы с пагинацией
        results = collection.get(
            limit=per_page,
            offset=(page - 1) * per_page,
            include=["documents", "metadatas"]
        )
        
        total_count = collection.count()
        total_pages = (total_count + per_page - 1) // per_page
        
        chunks_data = []
        for i in range(len(results["documents"])):
            chunks_data.append({
                "id": results["ids"][i],
                "document": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        
        return render_template('chunks.html', 
                             chunks=chunks_data,
                             page=page,
                             per_page=per_page,
                             total_count=total_count,
                             total_pages=total_pages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search')
def search():
    """Страница поиска."""
    return render_template('search.html')


@app.route('/api/search', methods=['POST'])
def api_search():
    """API для поиска."""
    if not collection or not model:
        return jsonify({"error": "Коллекция или модель не загружены"}), 500
    
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        schema_filter = data.get('schema_filter')
        top_k = int(data.get('top_k', 5))
        
        if not query_text:
            return jsonify({"error": "Запрос не может быть пустым"}), 400
        
        # Строим where clause
        where = {}
        if schema_filter:
            where["schema"] = schema_filter
        
        # Генерируем эмбеддинг запроса
        query_embedding = model.encode([query_text], normalize_embeddings=True)[0]
        
        # Выполняем поиск
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where if where else None,
            include=["documents", "metadatas", "distances"],
        )
        
        # Форматируем результаты
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        
        return jsonify({
            "query": query_text,
            "schema_filter": schema_filter,
            "top_k": top_k,
            "results": formatted_results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chunks')
def api_chunks():
    """API для получения чанков."""
    if not collection:
        return jsonify({"error": "Коллекция не загружена"}), 500
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        results = collection.get(
            limit=per_page,
            offset=(page - 1) * per_page,
            include=["documents", "metadatas"]
        )
        
        total_count = collection.count()
        
        chunks_data = []
        for i in range(len(results["documents"])):
            chunks_data.append({
                "id": results["ids"][i],
                "document": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        
        return jsonify({
            "chunks": chunks_data,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": (total_count + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vectors')
def vectors():
    """Страница визуализации векторов."""
    return render_template('vectors.html')


@app.route('/settings')
def settings():
    """Страница настроек."""
    return render_template('settings.html')


@app.route('/api/settings')
def api_get_settings():
    """API для получения текущих настроек."""
    try:
        settings_data = {
            "chroma_db_path": Config.CHROMA_DB_PATH,
            "collection_name": Config.COLLECTION_NAME,
            "embedding_model": Config.EMBEDDING_MODEL,
            "flask_debug": Config.DEBUG,
            "flask_host": Config.HOST,
            "flask_port": Config.PORT
        }
        return jsonify(settings_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """API для обновления настроек."""
    try:
        data = request.get_json()
        
        # Обновляем переменные окружения
        if 'chroma_db_path' in data:
            os.environ['CHROMA_DB_PATH'] = data['chroma_db_path']
        if 'collection_name' in data:
            os.environ['COLLECTION_NAME'] = data['collection_name']
        if 'embedding_model' in data:
            os.environ['EMBEDDING_MODEL'] = data['embedding_model']
        if 'flask_debug' in data:
            os.environ['FLASK_DEBUG'] = str(data['flask_debug']).lower()
        if 'flask_host' in data:
            os.environ['FLASK_HOST'] = data['flask_host']
        if 'flask_port' in data:
            os.environ['FLASK_PORT'] = str(data['flask_port'])
        
        # Перезагружаем конфигурацию
        from importlib import reload
        import config
        reload(config)
        Config = config.Config
        
        return jsonify({"message": "Настройки обновлены", "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/validate-folder', methods=['POST'])
def api_validate_folder():
    """API для валидации папки с базой данных Chroma."""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path', '')
        
        if not folder_path:
            return jsonify({"valid": False, "message": "Путь к папке не указан"}), 400
        
        # Проверяем существование папки
        folder = Path(folder_path)
        if not folder.exists():
            return jsonify({"valid": False, "message": "Папка не существует"}), 200
        
        if not folder.is_dir():
            return jsonify({"valid": False, "message": "Указанный путь не является папкой"}), 200
        
        # Пытаемся подключиться к Chroma
        try:
            temp_client = chromadb.PersistentClient(path=str(folder))
            collections = temp_client.list_collections()
            
            return jsonify({
                "valid": True,
                "message": "Папка содержит валидную базу данных Chroma",
                "collections_count": len(collections),
                "collections": [{"name": col.name, "id": col.id} for col in collections]
            })
        except Exception as chroma_error:
            return jsonify({
                "valid": False,
                "message": f"Папка не содержит валидную базу данных Chroma: {str(chroma_error)}"
            }), 200
            
    except Exception as e:
        return jsonify({"valid": False, "message": f"Ошибка валидации: {str(e)}"}), 500


@app.route('/api/vectors')
def api_vectors():
    """API для получения векторов для визуализации."""
    if not collection:
        return jsonify({"error": "Коллекция не загружена"}), 500
    
    try:
        # Получаем параметры
        limit = int(request.args.get('limit', 100))  # Ограничиваем количество для производительности
        schema_filter = request.args.get('schema')
        
        # Строим where clause
        where = {}
        if schema_filter:
            where["schema"] = schema_filter
        
        # Получаем векторы
        results = collection.get(
            limit=limit,
            where=where if where else None,
            include=["embeddings", "metadatas", "documents"]
        )
        
        vectors_data = []
        for i in range(len(results["embeddings"])):
            # Берем только первые 2 измерения для 2D визуализации
            embedding = results["embeddings"][i]
            if len(embedding) >= 2:
                vectors_data.append({
                    "id": results["ids"][i],
                    "x": float(embedding[0]),
                    "y": float(embedding[1]),
                    "full_vector": [float(x) for x in embedding],  # Полный вектор для tooltip
                    "metadata": results["metadatas"][i],
                    "document_preview": results["documents"][i][:100] + "..." if len(results["documents"][i]) > 100 else results["documents"][i]
                })
        
        return jsonify({
            "vectors": vectors_data,
            "total_count": len(vectors_data),
            "schema_filter": schema_filter
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
