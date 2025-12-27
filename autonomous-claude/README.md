# Autonomous Claude Memory System

A complete memory and decision-making framework for autonomous AI agents.

## Architecture

### Short-term Memory (SQLite)
- **Location**: `/autonomous-claude/data/memory/short_term.db`
- **Purpose**: Working memory for recent context
- **Retention**: Last 50 entries (auto-managed)
- **Types**: action, observation, thought, goal

### Long-term Memory (Qdrant)
- **Location**: `localhost:6333`, collection `claude_memory`
- **Purpose**: Persistent knowledge with semantic search
- **Types**: fact, skill, preference, lesson, discovery
- **Features**: Vector embeddings, importance scoring, tagging

### Browser Automation
- **Screenshots**: `/autonomous-claude/data/screenshots/`
- **Format**: `{timestamp}_{action}.png` + `.meta` file
- **Integration**: Playwright, Puppeteer support

## Decision Loop

```
1. READ    → Query recent short-term memories (context)
2. QUERY   → Semantic search long-term memory (knowledge)
3. THINK   → Analyze and decide next action
4. ACT     → Execute decision
5. RECORD  → Write to short-term memory
6. LEARN   → Store significant insights to long-term memory
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r /autonomous-claude/requirements.txt
```

### 2. Start Qdrant (for long-term memory)

**Option A: Docker (Recommended)**
```bash
docker run -d -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

**Option B: Install locally**
```bash
# See: https://qdrant.tech/documentation/install/
```

### 3. Initialize Memory System

```bash
python3 /autonomous-claude/setup_memory.py
```

### 4. Test Installation

```bash
python3 /autonomous-claude/decision_loop.py
```

## Usage

### Basic Memory Operations

```python
from memory import short_term, long_term

# Short-term memory
short_term.add("action", "Navigated to homepage")
short_term.add("observation", "Found 5 errors in logs")
short_term.add("thought", "Need to investigate error patterns")
short_term.add("goal", "Fix all critical errors")

# Retrieve recent context
recent = short_term.get_recent(limit=20)
for memory in recent:
    print(f"[{memory['type']}] {memory['content']}")

# Long-term memory
long_term.add(
    content="Python regex: use r'' for raw strings to avoid escaping",
    memory_type="skill",
    tags=["python", "regex", "best-practice"],
    importance=7
)

# Semantic search
results = long_term.search("how to write regex in python", limit=5)
for result in results:
    print(f"{result['content']} (score: {result['score']:.3f})")
```

### Decision Loop

```python
from decision_loop import DecisionLoop

loop = DecisionLoop()

# Set a goal
short_term.add("goal", "Analyze and fix application errors")

# Run decision cycle
loop.run_cycle(
    situation="Found errors in application logs",
    task_query="error analysis patterns"
)

# Save important learnings
loop.save_learning(
    content="Application errors often cluster around database timeouts at peak hours",
    memory_type="discovery",
    importance=8,
    tags=["errors", "database", "performance"]
)
```

### Browser Automation

```python
from playwright.sync_api import sync_playwright
from browser import BrowserSession

browser_session = BrowserSession()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Every action should be followed by a screenshot
    page.goto('https://example.com')
    browser_session.record_action(
        action='navigate_to_example',
        url=page.url,
        title=page.title(),
        screenshot_data=page.screenshot()
    )

    page.click('button#submit')
    browser_session.record_action(
        action='click_submit',
        url=page.url,
        title=page.title(),
        screenshot_data=page.screenshot()
    )

    browser.close()

# Review recent actions
for screenshot in browser_session.get_recent_screenshots(limit=10):
    print(f"{screenshot['filename']}: {screenshot['action']}")
```

## Memory Best Practices

### Short-term Memory
- ✅ Record every significant action
- ✅ Note observations immediately
- ✅ Document reasoning (thoughts)
- ✅ Track active goals
- ❌ Don't store redundant information
- ❌ Don't record trivial actions

### Long-term Memory
- ✅ **facts**: Environmental discoveries, configuration details
- ✅ **skills**: Techniques, patterns, best practices
- ✅ **lessons**: What worked, what failed, why
- ✅ **discoveries**: Insights, realizations, connections
- ✅ **preferences**: User preferences, optimal strategies
- ❌ Don't store temporary/transient information
- ❌ Don't duplicate short-term memory entries

### Importance Scoring (1-10)
- **9-10**: Critical insights, major discoveries
- **7-8**: Valuable skills, important lessons
- **5-6**: Useful facts, minor insights
- **3-4**: Low-priority information
- **1-2**: Barely worth storing

## Directory Structure

```
/autonomous-claude/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── setup_memory.py             # Initialize databases
├── memory.py                   # Memory interface
├── decision_loop.py            # Decision framework
├── browser.py                  # Browser automation utilities
└── data/
    ├── memory/
    │   └── short_term.db       # SQLite database
    └── screenshots/            # Browser screenshots
        ├── {timestamp}_{action}.png
        └── {timestamp}_{action}.meta
```

## Advanced Features

### Memory Queries

```python
# Get specific memory types
recent_goals = short_term.get_by_type("goal", limit=10)
recent_actions = short_term.get_by_type("action", limit=20)

# Semantic search with filters
important_lessons = long_term.search(
    query="debugging strategies",
    limit=10,
    min_importance=7
)

# Review browser history
screenshots = browser_session.get_recent_screenshots(limit=20)
```

### Clean Up

```python
# Clear short-term memory (use with caution!)
short_term.clear()

# Long-term memory persists unless explicitly deleted
```

## Troubleshooting

### Qdrant Not Available
If you see "Qdrant not available":
1. Check if Qdrant is running: `curl http://localhost:6333/health`
2. Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`
3. Install client: `pip install qdrant-client`

### Missing Dependencies
```bash
pip install sqlite3 qdrant-client sentence-transformers
```

### Permission Errors
Ensure `/autonomous-claude/` directory has write permissions:
```bash
chmod -R 755 /autonomous-claude/
```

## Examples

See individual module files for complete examples:
- `memory.py` - Memory operations
- `decision_loop.py` - Decision cycle demo
- `browser.py` - Browser automation examples

## License

MIT License - See repository for details
