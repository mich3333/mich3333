# Agent Contracts & Responsibilities

**Purpose**: Define explicit input/output contracts for each agent to improve debuggability and maintainability.

---

## 🎯 **Manager Agent**

**Responsibility**: Breaks down user tasks into actionable plans

**Input**:
- `user_task` (str): Raw user request
- `context` (MissionContext): Shared state

**Output** (writes to MissionContext):
- `execution_plan` (dict): JSON with steps/strategy
- Updates `current_status` → "executing"

**Success Criteria**:
- Plan is valid JSON
- Plan contains actionable steps
- If parsing fails, uses fallback plan

**Failure Modes**:
- Invalid JSON → Falls back to default plan
- API timeout → Retries with exponential backoff (3x)

---

## 🔍 **Researcher Agent**

**Responsibility**: Gathers information relevant to the task

**Input**:
- `topic` (str): Research subject
- `context` (MissionContext): Shared state

**Output** (writes to MissionContext):
- `shared_findings.research_data[topic]` (str): Research results
- `shared_findings.metadata['last_research']` (str): Topic key

**Success Criteria**:
- Data written to shared_findings
- No duplicate research (checks existing keys)

**Failure Modes**:
- API failure → Returns error, orchestrator continues
- Empty response → Logs warning, stores empty string

---

## 💻 **Coder Agent**

**Responsibility**: Writes code based on task and review feedback

**Input**:
- `task` (str): Coding task description
- `language` (str): Target programming language
- `context` (MissionContext): Shared state (reads `review_feedback`)

**Output** (writes to MissionContext):
- `shared_findings.code_artifacts[key]` (str): Generated code
- Key format: `{language}_{timestamp}`

**Success Criteria**:
- Code is syntactically valid (best effort)
- Incorporates review feedback if present
- Stored with unique timestamp key

**Failure Modes**:
- API failure → Retries 3x with backoff
- Review feedback loop → Max 2 iterations (hard limit)

**Special Behavior**:
- Reads `shared_findings.review_feedback[]` on retry
- Prepends feedback to prompt: "CRITICAL: Address this..."

---

## 🔎 **Reviewer Agent**

**Responsibility**: Reviews code quality and provides feedback

**Input**:
- `task_description` (str): Original coding task
- `context` (MissionContext): Shared state (reads latest code)

**Output**:
- Returns tuple: `(AgentResponse, ReviewDecision)`
- `ReviewDecision` enum: APPROVED | REJECTED | NEEDS_REVISION
- Writes `shared_findings.review_feedback[]` if not approved
- Updates `context.review_decision`

**Success Criteria**:
- Decision extracted from review text (keyword search)
- Feedback is actionable (extracted from review)

**Failure Modes**:
- Ambiguous review → Defaults to NEEDS_REVISION
- API failure → Returns error, orchestrator stops loop
- No code to review → Returns error

**Decision Logic** (reviewer.py:140-148):
```python
if "APPROVED" in review_text.upper():
    return ReviewDecision.APPROVED
elif "REJECTED" in review_text.upper():
    return ReviewDecision.REJECTED
else:
    return ReviewDecision.NEEDS_REVISION  # Safe default
```

---

## 📊 **Reporter Agent**

**Responsibility**: Generates final summary report

**Input**:
- `task` (str): Original user task
- `context` (MissionContext): Full shared state

**Output**:
- Returns `AgentResponse` with final report
- Report includes: task, plan, findings, code, decision

**Success Criteria**:
- Report includes all relevant MissionContext data
- Markdown formatted
- Readable by non-technical users

**Failure Modes**:
- Missing context data → Reports "N/A"
- API failure → Returns error with partial context

---

## 🔄 **Feedback Loop Guardrails**

### **Coder → Reviewer Loop**

**Stop Conditions** (in order of priority):
1. ✅ **APPROVED** → Exit immediately
2. ❌ **Max iterations reached** (2) → Exit with warning
3. 💥 **API failure** → Exit with error
4. 🛑 **Task cancelled** → Exit immediately

**Loop State Tracking**:
- `context.review_iteration` (int): Current iteration count
- `context.max_iterations` (int): Hard limit (default: 2)
- `context.review_decision` (ReviewDecision): Last decision

**Why 2 iterations?**
- Iteration 0: Initial code
- Iteration 1: Address first feedback
- Iteration 2: Address second feedback
- Beyond 2: Diminishing returns, potential infinite loop

**Escape Hatch**:
- Orchestrator checks `context.review_iteration >= max_iterations`
- Logs warning: "Max iterations reached. Proceeding with current version."
- This prevents infinite loops even if review keeps rejecting

---

## 📝 **MissionContext Lifecycle**

### **State Transitions**

```
┌─────────────┐
│  "planning" │  ← Initial state (Manager active)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ "executing" │  ← Running agents (Researcher, Coder)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ "reviewing" │  ← Feedback loop active (Coder ↔ Reviewer)
└──────┬──────┘
       │
       ├──→ "completed"  ← Success (all agents done)
       ├──→ "failed"     ← Error (agent failure)
       └──→ "cancelled"  ← User cancelled (kill switch)
```

### **Immutable Fields**
- `task_id`: Never changes
- `original_prompt`: Never changes

### **Mutable Fields**
- `current_status`: Updated by orchestrator
- `current_agent`: Updated before each agent call
- `agent_logs[]`: Append-only
- `shared_findings.*`: Written by agents
- `review_iteration`: Incremented in feedback loop

### **When to Read vs Write**

| Agent | Reads | Writes |
|-------|-------|--------|
| Manager | `original_prompt` | `execution_plan`, `current_status` |
| Researcher | `execution_plan` | `shared_findings.research_data` |
| Coder | `execution_plan`, `review_feedback` | `shared_findings.code_artifacts` |
| Reviewer | `code_artifacts` | `review_decision`, `review_feedback` |
| Reporter | All fields | (none - read-only) |

---

## 🚫 **What This System Does NOT Solve**

### **Explicit Trade-offs**

1. **No Code Execution**
   - System generates code but doesn't run it
   - No sandbox environment
   - **Why**: Security risk, complexity
   - **Future**: Could add Docker sandbox

2. **No Multi-Language Support**
   - Hardcoded to Python in orchestrator
   - **Why**: Simplicity, demo focus
   - **Future**: Add `language` parameter

3. **No Persistent Storage**
   - MissionContext lives in memory only
   - **Why**: Demo/prototype phase
   - **Future**: Add database (SQLite/Postgres)

4. **No Parallel Agent Execution**
   - Agents run sequentially
   - **Why**: Simpler logic, easier debugging
   - **Future**: Use asyncio.gather() for parallel research

5. **No Human-in-the-Loop**
   - Feedback loop is fully automated
   - **Why**: Demo autonomy
   - **Future**: Add approval gates

6. **Limited Error Recovery**
   - Failures stop the entire pipeline
   - **Why**: Fail-fast for debugging
   - **Future**: Add partial failure handling

7. **No Cost Controls**
   - No token limits or budget caps
   - **Why**: Prototype
   - **Future**: Add max_tokens per agent

---

## 🎙️ **2-Minute Verbal Explanation**

> "This is a multi-agent system where 5 specialized AI agents collaborate on tasks. Each agent has a clear contract: Manager plans, Researcher gathers info, Coder writes code, Reviewer checks quality, and Reporter summarizes.
>
> The key innovation is the **feedback loop** between Coder and Reviewer. If the code isn't good enough, Reviewer sends it back to Coder with specific feedback. We limit this to 2 iterations to prevent infinite loops.
>
> All agents share a **MissionContext** - think of it as a shared whiteboard. Agents write their outputs here and read what others wrote. This enables collaboration without tight coupling.
>
> We deliberately **don't** execute code or store data long-term. It's a prototype focused on demonstrating multi-agent coordination. The architecture is production-ready in terms of code quality, but would need sandboxing and persistence for real deployment."

---

## 🔧 **Interview Question Prep**

**Q: "What happens if Reviewer keeps rejecting code?"**
A: "We have a hard limit of 2 iterations. After that, we proceed with the current version and log a warning. This prevents infinite loops while still allowing quality improvement."

**Q: "How do agents communicate?"**
A: "Through MissionContext, a Pydantic model that acts as shared memory. Each agent reads what it needs and writes its outputs. It's validated end-to-end with type safety."

**Q: "What if an API call fails?"**
A: "Each agent has exponential backoff retry (1s → 2s → 4s). After 3 failures, we return an error and the orchestrator decides whether to continue or abort."

**Q: "Why not execute the generated code?"**
A: "Security and scope. Executing arbitrary AI-generated code requires sandboxing (Docker, Firecracker). This prototype focuses on multi-agent coordination patterns, not code execution safety."

**Q: "How would you add a new agent?"**
A: "Three steps: (1) Create agent class inheriting BaseAgent, (2) Add to orchestrator.__init__, (3) Call in execute_task(). The shared MissionContext automatically works."

---

**Document Version**: 1.0
**Last Updated**: 2026-01-04
**Authors**: Full Stack Developer Team
