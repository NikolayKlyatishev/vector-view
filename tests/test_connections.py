#!/usr/bin/env python3
"""
Тесты для системы управления подключениями.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vector_view.connections import ConnectionManager, ConnectionConfig


def test_connection_config():
    """Test ConnectionConfig creation and serialization."""
    config = ConnectionConfig(
        id="test-id",
        name="Test Connection",
        db_path="/test/path",
        collection_name="test-collection",
        embedding_model="test-model",
    )

    assert config.id == "test-id"
    assert config.name == "Test Connection"
    assert config.db_path == "/test/path"
    assert config.collection_name == "test-collection"
    assert config.embedding_model == "test-model"

    # Test serialization
    config_dict = config.to_dict()
    assert config_dict["id"] == "test-id"
    assert config_dict["name"] == "Test Connection"

    # Test deserialization
    config2 = ConnectionConfig.from_dict(config_dict)
    assert config2.id == config.id
    assert config2.name == config.name


def test_connection_manager_initialization():
    """Test ConnectionManager initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_connections.json")
        manager = ConnectionManager(config_file)

        assert manager.config_file == Path(config_file)
        assert len(manager.connections) == 0
        assert manager.active_connection_id is None
        assert not manager.is_connected()


def test_connection_crud_operations():
    """Test CRUD operations for connections."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_connections.json")
        manager = ConnectionManager(config_file)

        # Create connection
        config = ConnectionConfig(
            id="test-1",
            name="Test DB",
            db_path="/test/path",
            collection_name="test-collection",
            embedding_model="test-model",
        )

        conn_id = manager.add_connection(config)
        assert conn_id == "test-1"
        assert len(manager.connections) == 1

        # Get connection
        retrieved = manager.get_connection("test-1")
        assert retrieved is not None
        assert retrieved.name == "Test DB"

        # List connections
        connections = manager.list_connections()
        assert len(connections) == 1
        assert connections[0].name == "Test DB"

        # Update connection
        config.name = "Updated Test DB"
        success = manager.update_connection("test-1", config)
        assert success

        updated = manager.get_connection("test-1")
        assert updated.name == "Updated Test DB"

        # Delete connection
        success = manager.delete_connection("test-1")
        assert success
        assert len(manager.connections) == 0


def test_connection_manager_status():
    """Test connection manager status reporting."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_connections.json")
        manager = ConnectionManager(config_file)

        status = manager.get_status()
        assert isinstance(status, dict)
        assert "is_connected" in status
        assert "active_connection_id" in status
        assert "active_connection" in status
        assert "total_connections" in status
        assert "connections" in status

        assert status["is_connected"] is False
        assert status["active_connection_id"] is None
        assert status["total_connections"] == 0


def test_connection_validation():
    """Test connection validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_connections.json")
        manager = ConnectionManager(config_file)

        # Test invalid path
        validation = manager.validate_connection("", "test-collection")
        assert not validation["valid"]
        assert "не указан" in validation["message"]

        # Test non-existent path
        validation = manager.validate_connection(
            "/non/existent/path", "test-collection"
        )
        assert not validation["valid"]
        assert "не существует" in validation["message"]

        # Test file instead of directory
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test")

        validation = manager.validate_connection(test_file, "test-collection")
        assert not validation["valid"]
        assert "не является папкой" in validation["message"]


def test_connection_manager_persistence():
    """Test connection manager persistence."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_connections.json")

        # Create manager and add connection
        manager1 = ConnectionManager(config_file)
        config = ConnectionConfig(
            id="test-1",
            name="Test DB",
            db_path="/test/path",
            collection_name="test-collection",
            embedding_model="test-model",
        )
        manager1.add_connection(config)

        # Create new manager and load connections
        manager2 = ConnectionManager(config_file)
        assert len(manager2.connections) == 1
        assert manager2.get_connection("test-1").name == "Test DB"


if __name__ == "__main__":
    pytest.main([__file__])
