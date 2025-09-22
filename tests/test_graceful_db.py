#!/usr/bin/env python3
"""
Тесты для graceful handling отсутствующей БД.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vector_view.database import DatabaseManager
from vector_view.config import Config


def test_database_manager_initialization():
    """Test DatabaseManager initialization without DB."""
    db_manager = DatabaseManager()

    # Initially not initialized
    assert not db_manager.is_initialized
    assert db_manager.client is None
    assert db_manager.collection is None
    assert db_manager.model is None
    assert db_manager.initialization_error is None


def test_database_status():
    """Test database status reporting."""
    db_manager = DatabaseManager()

    status = db_manager.get_status()
    assert isinstance(status, dict)
    assert "is_initialized" in status
    assert "has_client" in status
    assert "has_collection" in status
    assert "has_model" in status
    assert "error" in status

    assert status["is_initialized"] is False
    assert status["has_client"] is False
    assert status["has_collection"] is False
    assert status["has_model"] is False


def test_database_availability_check():
    """Test database availability check."""
    db_manager = DatabaseManager()

    # Should return False when not initialized
    assert not db_manager.is_db_available()


def test_config_validation():
    """Test config validation with non-existent path."""
    # Test with non-existent path
    original_path = Config.CHROMA_DB_PATH
    Config.CHROMA_DB_PATH = "/non/existent/path"

    try:
        result = Config.validate_config()
        assert result is False
    finally:
        Config.CHROMA_DB_PATH = original_path


def test_graceful_error_handling():
    """Test graceful error handling in database operations."""
    db_manager = DatabaseManager()

    # Test get_collections without initialization
    with pytest.raises(RuntimeError) as exc_info:
        db_manager.get_collections()

    assert "База данных недоступна" in str(exc_info.value)

    # Test get_chunks without initialization
    with pytest.raises(RuntimeError) as exc_info:
        db_manager.get_chunks()

    assert "База данных недоступна" in str(exc_info.value)

    # Test search without initialization
    with pytest.raises(RuntimeError) as exc_info:
        db_manager.search("test query")

    assert "База данных недоступна" in str(exc_info.value)

    # Test get_vectors without initialization
    with pytest.raises(RuntimeError) as exc_info:
        db_manager.get_vectors()

    assert "База данных недоступна" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
