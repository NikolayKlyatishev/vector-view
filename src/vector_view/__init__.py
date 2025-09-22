"""
Vector View - A modern web interface for visualizing and interacting with vector databases.

A Flask-based web application for exploring ChromaDB collections, performing semantic search,
and visualizing vector embeddings in RAG (Retrieval-Augmented Generation) systems.
"""

__version__ = "1.0.0"
__author__ = "Vector View Contributors"
__email__ = "your-email@example.com"

from .app import app, init_app
from .config import Config

__all__ = ["app", "init_app", "Config"]
