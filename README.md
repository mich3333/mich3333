# 🤖 Multi-Agent System

> A sophisticated multi-agent AI system powered by Claude Opus 4.5, where specialized agents collaborate to solve complex tasks.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Claude Opus 4.5](https://img.shields.io/badge/Claude-Opus%204.5-purple.svg)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **🎯 Manager Agent** - Analyzes tasks and coordinates the team
- **🔍 Researcher Agent** - Gathers information and performs analysis
- **💻 Coder Agent** - Implements solutions with clean, efficient code
- **✅ Reviewer Agent** - Ensures quality through thorough code review
- **📊 Reporter Agent** - Creates comprehensive documentation

### Key Capabilities

✅ **Intelligent Task Decomposition** - Automatically breaks down complex tasks
✅ **Specialized Expertise** - Each agent has domain-specific knowledge
✅ **Collaborative Workflow** - Agents work together seamlessly
✅ **Real-Time Updates** - Watch agents work in real-time
✅ **Beautiful UI** - Modern, responsive interface
✅ **Production Ready** - Clean code, tests, documentation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-agent-system.git
cd multi-agent-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the App

```bash
# Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Run the Flask app
python app.py

# Open in browser
# http://localhost:5000
```

---

## 📖 Usage

### Example Tasks

**Software Development:**
```
Build a REST API for a todo app with:
- CRUD operations
- Authentication (JWT)
- SQLite database
- Unit tests
- API documentation
```

**Data Analysis:**
```
Create a Python script that:
- Fetches stock data for AAPL, GOOGL, MSFT
- Analyzes trends over the past 30 days
- Generates a comparison report with visualizations
```

**Documentation:**
```
Write comprehensive documentation for a Python library that:
- Includes getting started guide
- API reference
- Code examples
- Best practices
```

### How It Works

```
User Task
    ↓
┌─────────────────┐
│  Manager Agent  │  ← Analyzes & breaks down task
└─────────────────┘
    ↓
┌─────┬─────┬─────┬─────┐
│  🔍 │ 💻  │ ✅  │ 📊  │  ← Specialized agents execute
└─────┴─────┴─────┴─────┘
    ↓
┌─────────────────┐
│  Final Report   │  ← Comprehensive results
└─────────────────┘
```

---

## 🏗️ Architecture

```
multi-agent-system/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Base agent class
│   ├── manager.py          # Task coordinator
│   ├── researcher.py       # Information gathering
│   ├── coder.py           # Code implementation
│   ├── reviewer.py        # Quality assurance
│   └── reporter.py        # Documentation
├── orchestrator.py         # Coordinates agent workflow
├── app.py                 # Flask web application
├── templates/
│   └── index.html         # UI
├── static/
│   ├── css/style.css      # Styling
│   └── js/app.js          # Frontend logic
├── tests/
│   └── test_agents.py     # Unit tests
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

---

## 🛠️ API Endpoints

### `GET /api/status`
Get system and agent status.

**Response:**
```json
{
  "status": "online",
  "agents": {...},
  "anthropic_key_set": true
}
```

### `POST /api/execute`
Execute a task with the multi-agent system.

**Request:**
```json
{
  "task": "Your complex task here"
}
```

**Response:**
```json
{
  "task": "...",
  "plan": {...},
  "subtask_results": {...},
  "final_report": "...",
  "execution_log": [...],
  "status": "completed"
}
```

### `GET /api/agents`
Get information about all available agents.

### `POST /api/reset`
Reset all agents' conversation history.

---

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html
```

---

## 🚢 Deployment

### Render

1. Create new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set environment variable: `ANTHROPIC_API_KEY`
4. Deploy!

### Docker

```bash
# Build image
docker build -t multi-agent-system .

# Run container
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY=your-key \
  multi-agent-system
```

---

## 💡 Advanced Usage

### Custom Agents

Create your own specialized agent:

```python
from agents.base_agent import BaseAgent

class DataScientistAgent(BaseAgent):
    def __init__(self, **kwargs):
        system_prompt = """You are a Data Scientist Agent..."""

        super().__init__(
            name="Data Scientist",
            role="Data Analysis & ML",
            system_prompt=system_prompt,
            **kwargs
        )
```

### Programmatic Usage

```python
from orchestrator import MultiAgentOrchestrator

# Initialize
orch = MultiAgentOrchestrator(api_key="your-key")

# Execute task
result = orch.execute_task("Build a Flask API...")

# Access results
print(result['final_report'])
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- Built with [Anthropic Claude Opus 4.5](https://anthropic.com)
- Inspired by multi-agent AI research
- UI design inspired by modern web applications

---

## 📧 Contact

Questions? Issues? Reach out:
- GitHub Issues: [Create an issue](https://github.com/yourusername/multi-agent-system/issues)
- Email: your@email.com

---

**Made with ❤️ and 🤖**
