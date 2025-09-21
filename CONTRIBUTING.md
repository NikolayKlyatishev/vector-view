# Contributing to Vector View

Thank you for your interest in contributing to Vector View! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A modern web browser (Chrome/Edge recommended for folder selection)

### Development Setup

1. **Fork and clone the repository**
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

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

### Commit Messages

Use clear, descriptive commit messages:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `style: format code`
- `refactor: improve code structure`
- `test: add tests`

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Test your changes thoroughly
   - Update documentation if needed

3. **Test your changes**
   ```bash
   make test  # Run tests
   make web   # Test the application
   ```

4. **Submit a pull request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Include screenshots for UI changes

## Project Structure

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
├── CONTRIBUTING.md       # This file
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── settings.html     # Settings page
    ├── collections.html  # Collections page
    ├── chunks.html       # Chunks page
    ├── search.html       # Search page
    └── vectors.html      # Vectors visualization
```

## Areas for Contribution

### High Priority
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve API documentation
- **Performance**: Optimize vector operations
- **UI/UX**: Enhance user interface

### Medium Priority
- **Features**: Add new visualization options
- **Configuration**: More configuration options
- **Error Handling**: Better error messages
- **Accessibility**: Improve accessibility

### Low Priority
- **Internationalization**: Multi-language support
- **Themes**: Dark/light theme support
- **Plugins**: Plugin system
- **API**: RESTful API improvements

## Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Operating system
   - Python version
   - Browser version
   - Vector View version

2. **Steps to reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Error messages**
   - Full error traceback
   - Browser console errors
   - Server logs

## Feature Requests

When requesting features, please provide:

1. **Use case description**
   - What problem does it solve?
   - How would you use it?

2. **Proposed solution**
   - How should it work?
   - Any design considerations?

3. **Alternatives considered**
   - Other approaches you've thought about

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discrimination
- Personal attacks or political discussions
- Public or private harassment
- Publishing private information without permission
- Other unprofessional conduct

## Questions?

If you have questions about contributing, please:

1. Check the [Issues](https://github.com/your-username/vector-view/issues) page
2. Create a new issue with the "question" label
3. Join our discussions

Thank you for contributing to Vector View! 🚀
