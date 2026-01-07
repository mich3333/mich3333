# Quick Reference Guide

**Purpose**: 2-minute cheat sheet for code reviews, interviews, and onboarding.

---

## 🎯 **System Overview (30 seconds)**

**What It Does**:
Multi-agent AI system where 5 specialized agents collaborate on tasks.

**Key Innovation**:
Feedback loop between Coder and Reviewer ensures code quality (max 2 iterations).

**Tech Stack**:
- Backend: Python 3.11 + Flask + AsyncAnthropic
- Frontend: React 18 + TypeScript + Tailwind
- State: Pydantic v2 (MissionContext)
- Real-time: Flask-SocketIO

---

## 🔢 **Key Numbers**

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| **Agents** | 5 | Manager, Researcher, Coder, Reviewer, Reporter |
| **Max Iterations** | 2 | Prevents infinite loops in feedback |
| **API Retries** | 3 | Exponential backoff: 1s → 2s → 4s |
| **WebSocket Reconnect** | 5 | Frontend auto-reconnects max 5 times |
| **LOC** | 2,497 | Production-ready codebase |
| **Type Coverage** | 100% | Pydantic + TypeScript end-to-end |

---

## 🧠 **Agent Responsibilities (60 seconds)**

```
┌─────────────┐
│   Manager   │ → Breaks task into plan (JSON)
└──────┬──────┘
       ↓
┌─────────────┐
│ Researcher  │ → Gathers information
└──────┬──────┘
       ↓
┌─────────────┐      ┌─────────────┐
│   Coder     │ ←──→ │  Reviewer   │ (Feedback Loop, max 2 iterations)
└──────┬──────┘      └─────────────┘
       ↓
┌─────────────┐
│  Reporter   │ → Final summary
└─────────────┘
```

**Coder ↔ Reviewer Loop**:
1. Coder writes code
2. Reviewer checks quality → APPROVED | REJECTED | NEEDS_REVISION
3. If not APPROVED, go back to step 1 (max 2 retries)
4. Exit: either approved or max iterations reached

---

## 📦 **MissionContext (Shared State)**

**What It Is**: Centralized memory shared by all agents (like a whiteboard).

**Immutable Fields** (never change):
- `task_id`: Unique identifier
- `original_prompt`: User's request
- `created_at`: Timestamp

**Mutable Fields** (agents write here):
- `shared_findings.research_data{}`: Researcher's output
- `shared_findings.code_artifacts{}`: Coder's output
- `shared_findings.review_feedback[]`: Reviewer's feedback
- `execution_plan{}`: Manager's plan
- `review_decision`: APPROVED | REJECTED | NEEDS_REVISION

**State Transitions**:
```
"planning" → "executing" → "reviewing" → "completed" | "failed" | "cancelled"
```

---

## ⚠️ **Failure Modes & Guardrails**

### **Infinite Loop Prevention**
```python
# ✅ GOOD: Explicit max iterations
for iteration in range(max_iterations + 1):
    if decision == ReviewDecision.APPROVED:
        break  # Early exit

# ❌ BAD: No termination condition
while not approved:
    await coder.code(...)  # Can run forever
```

### **API Failure Handling**
```python
# Each agent retries 3 times with exponential backoff
for attempt in range(3):
    try:
        response = await api_call()
        return response
    except Exception:
        await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
```

### **WebSocket Safety**
```python
# Broadcast errors don't crash the system
try:
    socketio.emit('agent_update', data)
except Exception as e:
    print(f"WebSocket error: {e}")  # Log but continue
```

---

## 🎤 **Interview Q&A**

### **Q: What happens if Reviewer keeps rejecting code?**
**A**: "We have a hard limit of 2 iterations. After that, we proceed with the current version and log a warning. This prevents infinite loops while still allowing quality improvement. It's inspired by agile—most code reviews converge in 2 rounds."

---

### **Q: How do agents communicate?**
**A**: "Through MissionContext, a Pydantic model that acts as shared memory. Each agent reads what it needs (e.g., Coder reads `review_feedback`) and writes its outputs (e.g., `code_artifacts`). It's validated end-to-end with type safety. We chose shared state over message passing for simplicity and observability in this prototype."

---

### **Q: What if an API call fails?**
**A**: "Each agent has exponential backoff retry—1s, 2s, 4s. After 3 failures, we return an error. The orchestrator decides whether to continue (for non-critical agents like Researcher) or abort (for critical agents like Manager). We fail fast to surface issues early."

---

### **Q: Why not execute the generated code?**
**A**: "Security and scope. Executing arbitrary AI-generated code requires sandboxing—Docker, resource limits, network policies. This prototype focuses on multi-agent coordination patterns, not code execution safety. In production, we'd integrate with an existing sandbox service like AWS Lambda."

---

### **Q: How would you scale this to 1000 concurrent users?**
**A**:
1. **Persistence**: Migrate MissionContext from memory to PostgreSQL + Redis
2. **Async Workers**: Move agents to Celery workers (distributed queue)
3. **WebSocket**: Add Redis pub/sub for multi-instance support
4. **Caching**: Cache Claude API responses (dedupe similar prompts)
5. **Rate Limiting**: Add token budget per user
6. **Monitoring**: Add Prometheus metrics for latency, success rate

---

### **Q: What's your testing strategy?**
**A**: "Three levels:
1. **Unit**: Mock API calls, test agent logic in isolation
2. **Integration**: Test MissionContext validation with Pydantic
3. **E2E**: Test full orchestrator flow with real API (in CI)

We also have linters (Ruff, ESLint) and type checking (Pydantic, TypeScript) as pre-commit hooks."

---

## 🚀 **Deployment Checklist**

### **Environment Variables**
```bash
ANTHROPIC_API_KEY=sk-ant-xxx  # Required
FLASK_ENV=production           # Required
PORT=10000                     # Optional (default: 5000)
```

### **Pre-Deploy Steps**
```bash
# Backend
cd multi-agent-system
ruff check .               # Lint
python -m pytest           # Tests

# Frontend
cd frontend
npm run lint               # ESLint
npm run typecheck          # TypeScript
npm run build              # Production build

# Docker
docker-compose up --build  # Full stack test
```

### **Post-Deploy Verification**
```bash
# Health check
curl http://localhost:5000/health

# WebSocket test
wscat -c ws://localhost:5000/socket.io/?EIO=4&transport=websocket

# E2E test
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Write hello world in Python"}'
```

---

## 📁 **File Structure (Key Files)**

```
multi-agent-system/
├── models/
│   └── state.py              # MissionContext, AgentStatus, ReviewDecision
├── agents/
│   ├── base_agent.py         # Async base class with retry logic
│   ├── manager.py            # JSON plan generation
│   ├── researcher.py         # Research data gathering
│   ├── coder.py              # Code generation (reads feedback)
│   ├── reviewer.py           # Code review (writes feedback)
│   └── reporter.py           # Final summary
├── orchestrator.py           # Feedback loop orchestration
├── app.py                    # Flask + SocketIO server
├── AGENT_CONTRACTS.md        # Agent input/output specs
├── ARCHITECTURE.md           # ADRs (Architecture Decisions)
└── QUICK_REFERENCE.md        # This file
```

---

## 🔧 **Common Debugging Tips**

### **Agent Stuck in Loop**
```bash
# Check review_iteration count
grep "review_iteration" logs/app.log

# Should never exceed max_iterations (2)
# If it does, there's a bug in loop termination logic
```

### **WebSocket Not Connecting**
```bash
# Frontend: Check browser console
# Look for: "WebSocket connection failed"

# Backend: Check Flask logs
# Look for: "WebSocket connection from ..."

# Common fix: CORS headers missing
```

### **API Rate Limit Hit**
```bash
# Check for 429 errors in logs
grep "429" logs/app.log

# Temporary fix: Add sleep between requests
# Long-term: Implement token bucket rate limiter
```

---

## 📊 **Metrics to Monitor (Production)**

| Metric | Threshold | Action If Exceeded |
|--------|-----------|-------------------|
| **Avg Latency** | <30s | Parallelize independent agents |
| **API Error Rate** | <5% | Increase retry backoff |
| **Feedback Loop %** | <30% | Tune Reviewer prompts |
| **WebSocket Disconnect** | <10% | Increase reconnect attempts |
| **Memory per Task** | <100MB | Add cleanup logic |

---

## 🎓 **Learning Resources**

### **Anthropic Claude**
- [API Docs](https://docs.anthropic.com/)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

### **Multi-Agent Systems**
- [LangChain Multi-Agent Tutorial](https://python.langchain.com/docs/use_cases/multi_agent)
- [AutoGPT Architecture](https://github.com/Significant-Gravitas/AutoGPT)

### **Pydantic**
- [Pydantic V2 Docs](https://docs.pydantic.dev/latest/)
- [Validation Best Practices](https://docs.pydantic.dev/latest/concepts/validators/)

---

## 🏁 **TL;DR (Absolute Minimum)**

**What**: 5 AI agents (Manager, Researcher, Coder, Reviewer, Reporter) collaborate on tasks

**How**: Shared MissionContext (Pydantic) + Feedback Loop (Coder ↔ Reviewer, max 2 iterations)

**Tech**: Python AsyncAnthropic + React TypeScript + Flask-SocketIO

**Key Numbers**: 2,497 LOC | 5 Agents | Max 2 Iterations | 3 API Retries

**Guardrails**: Explicit loop termination | Exponential backoff | Type-safe end-to-end

**Deploy**: `docker-compose up` (all configs in `docker-compose.yml`)

---

**Print this page and keep it by your desk!** 📋
