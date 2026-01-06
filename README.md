# 🤖 Autonomous Claude

> AI-powered autonomous agent with memory, decision-making, and modern web interface

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

An intelligent autonomous agent powered by Claude AI, featuring a dual-memory system, real-time decision-making capabilities, and a beautiful modern web interface built with TypeScript and Tailwind CSS.

---

## ✨ Features

### 🧠 AI & Intelligence
- **Claude AI Integration** - Powered by Anthropic Claude for intelligent decision-making
- **Autonomous Agent** - Self-directed AI that can set and achieve goals
- **Decision Loop Framework** - READ → QUERY → THINK → ACT → RECORD → LEARN cycle
- **Learning System** - Learns from experience and improves over time

### 💾 Memory System
- **Dual-Layer Architecture**
  - **Short-term**: SQLite database with automatic cleanup
  - **Long-term**: Qdrant vector database for semantic search
- **Auto-cleanup**: Maintains optimal memory size automatically
- **Type-based organization**: Goals, thoughts, actions, observations

### 🌐 Web Interface
- **Modern Dashboard** - Interactive real-time control panel
- **Portfolio Landing Page** - Professional showcase with Tailwind CSS
- **TypeScript Frontend** - Type-safe, maintainable code (700+ lines)
- **REST API** - 12+ endpoints for complete control
- **Real-time Updates** - Live status and memory updates

### 🎨 Design Tools
- **Figma Integration** - Import designs directly from Figma
- **Auto-extract** - Colors, typography, and components
- **Code Generation** - Tailwind config and CSS variables
- **Component Export** - Convert Figma frames to HTML/CSS

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for TypeScript)
- Anthropic API Key (Claude Opus 4.5)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/autonomous-claude.git
cd autonomous-claude

# Install Python dependencies
cd autonomous-claude
pip install -r requirements.txt

# Set up environment variables
export ANTHROPIC_API_KEY='your-anthropic-api-key'
export FIGMA_TOKEN='your-figma-token'  # Optional

# Run the application
python3 web_app.py
```

### Access the Application

- **Portfolio**: http://localhost:5000/
- **Dashboard**: http://localhost:5000/dashboard
- **Showcase**: http://localhost:5000/showcase
- **API**: http://localhost:5000/api/status

---

## 📖 Documentation

### Project Structure

```
autonomous-claude/
├── autonomous_agent.py      # Main autonomous agent (261 lines)
├── claude_brain.py          # Claude Opus 4.5 integration (332 lines)
├── memory.py                # Memory system (266 lines)
├── decision_loop.py         # Decision framework (202 lines)
├── browser.py               # Browser automation (233 lines)
├── figma_integration.py     # Figma API client (330 lines)
├── web_app.py               # Flask server (350+ lines)
├── templates/
│   ├── index.html           # Dashboard UI
│   ├── portfolio.html       # Landing page
│   └── showcase.html        # Feature showcase
├── static/
│   ├── css/                 # Styles
│   ├── js/                  # Compiled JavaScript
│   └── ts/                  # TypeScript source (700+ lines)
├── tests/
│   ├── test_memory.py       # Memory tests
│   └── test_api.py          # API tests
└── requirements.txt         # Dependencies
```

### API Endpoints

#### Agent Control
```http
POST /api/agent/goal          # Set agent goal
POST /api/agent/start         # Start autonomous agent
POST /api/agent/stop          # Stop agent
GET  /api/status             # Get current status
```

#### Memory Management
```http
GET  /api/memories/recent    # Get recent memories
GET  /api/memories/search    # Search by type
GET  /api/memories/stats     # Memory statistics
POST /api/memories/add       # Add new memory
POST /api/database/clear     # Clear all memories
```

#### Claude AI
```http
POST /api/claude/think       # Ask Claude to think
POST /api/claude/analyze     # Analyze and decide
POST /api/claude/learn       # Learn from experience
```

#### Figma Integration
```http
POST /api/figma/import       # Import Figma design
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core language
- **Flask 3.0** - Web framework
- **SQLite** - Short-term memory database
- **Qdrant** - Vector database for semantic search
- **Anthropic API** - Claude Opus 4.5 integration

### Frontend
- **TypeScript 5.0+** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Vanilla JS** - No framework dependencies
- **Modern CSS** - Gradients, animations, responsive design

### AI & ML
- **Anthropic Claude Opus 4.5** - Language model
- **Sentence Transformers** - Text embeddings
- **Vector Search** - Semantic similarity

### Tools & Integration
- **Figma API** - Design import
- **REST API** - Integration-ready
- **CORS** - Cross-origin support
- **n8n Ready** - Workflow automation

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_memory.py -v
```

### Test Coverage
- ✅ Memory system tests
- ✅ API endpoint tests
- ✅ Integration tests
- ✅ Error handling tests

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | 2,680+ |
| **Core Modules** | 11 |
| **API Endpoints** | 12+ |
| **Test Coverage** | 85%+ |
| **Languages** | Python, TypeScript |
| **Commits** | 10+ |

---

## 🎯 Use Cases

### 1. Autonomous Research
```python
agent.set_goal("Research the latest AI developments")
agent.run()
# Agent autonomously searches, analyzes, and summarizes
```

### 2. Design Automation
```python
from figma_integration import FigmaClient

client = FigmaClient()
design = client.get_file('your-file-key')
colors = client.extract_colors(design)
# Auto-generate design system
```

### 3. Intelligent Assistant
```python
brain = ClaudeBrain()
decision = brain.think("How should I approach this problem?")
# Get intelligent recommendations
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...       # Anthropic API key

# Optional
FIGMA_TOKEN=figd_...               # Figma Personal Access Token
FLASK_ENV=development              # Flask environment
FLASK_APP=web_app.py               # Flask app entry point
```

### Memory Configuration

Edit `memory.py` to adjust:
- Memory retention limit (default: 50 entries)
- Database path
- Qdrant connection settings

---

## 📚 Learn More

- [Web Interface Guide](autonomous-claude/WEB_INTERFACE.md)
- [Figma Integration](autonomous-claude/FIGMA_INTEGRATION.md)
- [ChatGPT Setup](autonomous-claude/CHATGPT_SETUP.md)
- [API Documentation](#api-endpoints)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Built with ❤️ using Claude AI, TypeScript, and Python

---

## 🙏 Acknowledgments

- Anthropic for Claude AI API
- Figma for design integration API
- Qdrant for vector database
- Tailwind CSS for modern styling

---

## 🔗 Links

- **Documentation**: [View Docs](docs/)
- **Demo**: [Live Demo](#) <!-- Add your demo URL -->
- **GitHub**: [Repository](#) <!-- Add your GitHub URL -->
- **Issues**: [Report Bug](#) <!-- Add your issues URL -->

---

**Made with ⚡ by [Your Name]**
