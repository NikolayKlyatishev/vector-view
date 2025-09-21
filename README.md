# Vector View

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)

A modern web interface for visualizing and interacting with vector databases in RAG (Retrieval-Augmented Generation) systems. Built with Flask and ChromaDB.

## ✨ Features

- **📊 Collection Browser**: View and explore ChromaDB collections with metadata
- **📄 Document Chunks**: Browse indexed document chunks with pagination
- **🔍 Semantic Search**: Natural language search with filtering capabilities
- **📈 Vector Visualization**: Interactive 2D visualization of vector space
- **⚙️ Settings Management**: Easy configuration through web interface
- **📁 Folder Picker**: Modern folder selection using File System Access API
- **🌐 Multi-language Support**: Built-in support for multilingual embeddings

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A ChromaDB database with indexed documents

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/vector-view.git
   cd vector-view
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or use the Makefile
   make install
   ```

4. **Run the application**
   ```bash
   make web
   # or
   python run_web.py
   ```

5. **Open your browser**
   ```
   http://localhost:5001
   ```

## 📖 Usage

### Configuration

Vector View supports configuration through environment variables or the web interface:

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMA_DB_PATH` | `../.chroma` | Path to ChromaDB directory |
| `COLLECTION_NAME` | `usage-guides` | Collection name |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Embedding model |
| `FLASK_HOST` | `0.0.0.0` | Server host |
| `FLASK_PORT` | `5001` | Server port |
| `FLASK_DEBUG` | `True` | Debug mode |

### Examples

```bash
# Custom ChromaDB path
CHROMA_DB_PATH=/path/to/chroma make web

# Different collection
COLLECTION_NAME=my-collection make web

# Custom port
FLASK_PORT=8080 make web

# Combined settings
CHROMA_DB_PATH=/data/chroma COLLECTION_NAME=docs FLASK_PORT=3000 make web
```

## 🛠️ Development

### Project Structure

```
vector-view/
├── app.py                 # Main Flask application
├── run_web.py            # Application runner
├── config.py             # Configuration management
├── test_web.py           # Tests
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
├── Makefile              # Build commands
├── README.md             # Project documentation
├── LICENSE               # MIT License
├── CONTRIBUTING.md       # Contributing guidelines
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── settings.html     # Settings page
    ├── collections.html  # Collections page
    ├── chunks.html       # Chunks page
    ├── search.html       # Search page
    └── vectors.html      # Vectors visualization
```

### Available Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make web           # Run web interface
make test          # Run tests
make clean         # Clean virtual environment
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/collections` | GET | Collections page |
| `/api/collections` | GET | Collections API |
| `/chunks` | GET | Chunks page |
| `/api/chunks` | GET | Chunks API |
| `/search` | GET | Search page |
| `/api/search` | POST | Search API |
| `/vectors` | GET | Vectors page |
| `/api/vectors` | GET | Vectors API |
| `/settings` | GET | Settings page |
| `/api/settings` | GET/POST | Settings API |
| `/api/validate-folder` | POST | Folder validation API |

## 🔧 Configuration

### Web Interface

1. Navigate to **Settings** in the web interface
2. Configure your ChromaDB path using the folder picker
3. Set your collection name and embedding model
4. Adjust server settings as needed
5. Save your configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
CHROMA_DB_PATH=/path/to/your/chroma
COLLECTION_NAME=your-collection
FLASK_PORT=8080
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [Bootstrap](https://getbootstrap.com/) - UI framework

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-username/vector-view/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/your-username/vector-view/discussions)
- 📧 **Questions**: Open an issue with the "question" label

## 🗺️ Roadmap

- [ ] Comprehensive test coverage
- [ ] Dark/light theme support
- [ ] Plugin system
- [ ] Multi-language UI
- [ ] Advanced vector analytics
- [ ] Real-time collaboration
- [ ] Export/import functionality

---

Made with ❤️ for the RAG community
