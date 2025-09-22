"""
Database management module for Vector View.

Handles ChromaDB client initialization and collection management.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from .connections import connection_manager


class DatabaseManager:
    """Manages ChromaDB client and collections."""

    def __init__(self):
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection = None
        self.model: Optional[SentenceTransformer] = None
        self.is_initialized = False
        self.initialization_error: Optional[str] = None

    def load_chroma_collection(self, db_path: Path, collection_name: str):
        """Load Chroma collection from persistent storage."""
        try:
            self.client = chromadb.PersistentClient(path=str(db_path))
            self.collection = self.client.get_collection(collection_name)
            self.is_initialized = True
            self.initialization_error = None
            return self.collection
        except Exception as e:
            self.is_initialized = False
            self.initialization_error = (
                f"Ошибка загрузки коллекции '{collection_name}': {e}"
            )
            raise RuntimeError(self.initialization_error) from e

    def load_embedding_model(self, model_name: str):
        """Load sentence transformer model."""
        try:
            self.model = SentenceTransformer(model_name)
            return self.model
        except Exception as e:
            self.is_initialized = False
            self.initialization_error = f"Ошибка загрузки модели '{model_name}': {e}"
            raise RuntimeError(self.initialization_error) from e

    def is_db_available(self) -> bool:
        """Check if database is available and initialized."""
        return self.is_initialized and self.client is not None

    def use_connection_manager(self) -> bool:
        """Use connection manager instead of direct connection."""
        if connection_manager.is_connected():
            self.client = connection_manager.current_client
            self.collection = connection_manager.current_collection
            self.model = connection_manager.current_model
            self.is_initialized = True
            self.initialization_error = None
            return True
        return False

    def get_status(self) -> dict:
        """Get current database status."""
        return {
            "is_initialized": self.is_initialized,
            "has_client": self.client is not None,
            "has_collection": self.collection is not None,
            "has_model": self.model is not None,
            "error": self.initialization_error,
        }

    def get_collections(self):
        """Get list of all collections."""
        # Try to use connection manager first
        if not self.is_db_available() and not self.use_connection_manager():
            raise RuntimeError(
                f"База данных недоступна. {self.initialization_error or 'Не инициализирована'}"
            )

        collections_list = self.client.list_collections()
        collections_data = []

        for col in collections_list:
            col_data = {"name": col.name, "id": col.id, "metadata": col.metadata or {}}
            try:
                count = col.count()
                col_data["document_count"] = count
            except:
                col_data["document_count"] = "Неизвестно"

            collections_data.append(col_data)

        return collections_data

    def get_chunks(self, page: int = 1, per_page: int = 20):
        """Get document chunks with pagination."""
        # Try to use connection manager first
        if not self.is_db_available() and not self.use_connection_manager():
            raise RuntimeError(
                f"База данных недоступна. {self.initialization_error or 'Не инициализирована'}"
            )

        results = self.collection.get(
            limit=per_page,
            offset=(page - 1) * per_page,
            include=["documents", "metadatas"],
        )

        total_count = self.collection.count()
        total_pages = (total_count + per_page - 1) // per_page

        chunks_data = []
        for i in range(len(results["documents"])):
            chunks_data.append(
                {
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
            )

        return {
            "chunks": chunks_data,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
        }

    def search(
        self, query_text: str, schema_filter: Optional[str] = None, top_k: int = 5
    ):
        """Perform semantic search."""
        # Try to use connection manager first
        if not self.is_db_available() and not self.use_connection_manager():
            raise RuntimeError(
                f"База данных недоступна. {self.initialization_error or 'Не инициализирована'}"
            )
        if not self.model:
            raise RuntimeError("Модель эмбеддингов не загружена")

        if not query_text:
            raise ValueError("Запрос не может быть пустым")

        # Build where clause
        where = {}
        if schema_filter:
            where["schema"] = schema_filter

        # Generate query embedding
        query_embedding = self.model.encode([query_text], normalize_embeddings=True)[0]

        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where if where else None,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append(
                {
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        return {
            "query": query_text,
            "schema_filter": schema_filter,
            "top_k": top_k,
            "results": formatted_results,
        }

    def get_vectors(self, limit: int = 100, schema_filter: Optional[str] = None):
        """Get vectors for visualization."""
        # Try to use connection manager first
        if not self.is_db_available() and not self.use_connection_manager():
            raise RuntimeError(
                f"База данных недоступна. {self.initialization_error or 'Не инициализирована'}"
            )

        # Build where clause
        where = {}
        if schema_filter:
            where["schema"] = schema_filter

        # Get vectors
        results = self.collection.get(
            limit=limit,
            where=where if where else None,
            include=["embeddings", "metadatas", "documents"],
        )

        vectors_data = []
        for i in range(len(results["embeddings"])):
            # Take only first 2 dimensions for 2D visualization
            embedding = results["embeddings"][i]
            if len(embedding) >= 2:
                vectors_data.append(
                    {
                        "id": results["ids"][i],
                        "x": float(embedding[0]),
                        "y": float(embedding[1]),
                        "full_vector": [float(x) for x in embedding],
                        "metadata": results["metadatas"][i],
                        "document_preview": (
                            results["documents"][i][:100] + "..."
                            if len(results["documents"][i]) > 100
                            else results["documents"][i]
                        ),
                    }
                )

        return {
            "vectors": vectors_data,
            "total_count": len(vectors_data),
            "schema_filter": schema_filter,
        }

    def validate_chroma_folder(self, folder_path: str):
        """Validate ChromaDB folder."""
        if not folder_path:
            return {"valid": False, "message": "Путь к папке не указан"}

        folder = Path(folder_path)
        if not folder.exists():
            return {"valid": False, "message": "Папка не существует"}

        if not folder.is_dir():
            return {"valid": False, "message": "Указанный путь не является папкой"}

        # Try to connect to Chroma
        try:
            temp_client = chromadb.PersistentClient(path=str(folder))
            collections = temp_client.list_collections()

            return {
                "valid": True,
                "message": "Папка содержит валидную базу данных Chroma",
                "collections_count": len(collections),
                "collections": [
                    {"name": col.name, "id": col.id} for col in collections
                ],
            }
        except Exception as chroma_error:
            return {
                "valid": False,
                "message": f"Папка не содержит валидную базу данных Chroma: {str(chroma_error)}",
            }


# Global database manager instance
db_manager = DatabaseManager()
