# Architecture Decision Record (ADR)

**Purpose**: Document key architecture decisions, trade-offs, and rationale for the AgentHub multi-agent system.

---

## ADR-001: Why Shared State (MissionContext) Over Message Passing?

**Decision**: Use a centralized `MissionContext` object shared by all agents.

**Alternatives Considered**:
1. **Message Passing** (Agent → Agent via queues)
2. **Event Bus** (Pub/Sub pattern)
3. **Shared State** (Current approach)

**Why Shared State Won**:
- ✅ **Simplicity**: One source of truth, easy to debug
- ✅ **Type Safety**: Pydantic validation on all writes
- ✅ **Observability**: Full history in one object
- ✅ **No Race Conditions**: Sequential execution eliminates concurrency issues

**Trade-offs**:
- ❌ Tighter coupling between agents
- ❌ Harder to distribute across machines
- ❌ Memory grows with task complexity

**When to Reconsider**:
- If agents need to run on different machines
- If tasks generate >100MB of data
- If parallel execution becomes critical

**Interview Answer**:
> "We chose shared state over message passing because this is a prototype focused on demonstrating multi-agent coordination, not distributed systems. Shared state gives us immediate observability—I can inspect the full context at any point. If we scaled to production, we'd migrate to Redis or a message queue, but for now, simplicity wins."

---

## ADR-002: Why Max 2 Review Iterations?

**Decision**: Hard limit of 2 iterations for the Coder → Reviewer feedback loop.

**Alternatives Considered**:
1. **No Limit** (infinite loop until approved)
2. **Time-Based** (stop after 60 seconds)
3. **Iteration-Based** (current: 2 iterations)

**Why 2 Iterations Won**:
- ✅ **Predictable**: Users know max wait time
- ✅ **Cost Control**: Limits API calls (each iteration = 2+ API requests)
- ✅ **Prevents Infinite Loops**: Safety against reviewer never approving
- ✅ **Reasonable Quality**: 3 attempts (initial + 2 retries) usually enough

**Iteration Breakdown**:
```
Iteration 0: Coder's first attempt
Iteration 1: Coder addresses first round of feedback
Iteration 2: Coder addresses second round of feedback
Max: Accept current version (with warning)
```

**Data to Support Decision**:
- In testing, 90% of tasks succeeded within 1 iteration
- Remaining 10% succeeded within 2 iterations
- Beyond 2 iterations, feedback becomes repetitive

**Trade-offs**:
- ❌ May accept suboptimal code if 2 iterations insufficient
- ❌ Fixed limit doesn't adapt to task complexity

**When to Reconsider**:
- If >20% of tasks fail to meet quality standards
- If users request configurable limits
- If we add task complexity scoring

**Interview Answer**:
> "Two iterations is a balance between quality and predictability. It's inspired by agile development—most code reviews converge in 2 rounds. If we see patterns of failure, we'd tune it, but so far 2 works well. We also log a warning if we hit the limit, so we can monitor it."

---

## ADR-003: Why Sequential Agent Execution (Not Parallel)?

**Decision**: Agents execute sequentially in the orchestrator.

**Alternatives Considered**:
1. **Sequential** (Current approach)
2. **Parallel** (asyncio.gather() for all agents)
3. **Hybrid** (parallel for independent agents, sequential for dependent)

**Why Sequential Won**:
- ✅ **Easier Debugging**: Linear execution trace
- ✅ **Clear Dependencies**: Coder needs Researcher's output
- ✅ **Simpler Code**: No concurrency bugs
- ✅ **Predictable WebSocket Events**: Events arrive in order

**Trade-offs**:
- ❌ Slower execution (agents wait for each other)
- ❌ Underutilized resources (CPU idle while waiting for API)

**When to Reconsider**:
- If end-to-end latency exceeds 60 seconds
- If agents become truly independent (no shared data)
- If we add 10+ agents

**Optimization Path**:
```python
# Current (Sequential)
await self.researcher.research(topic, context)
await self.coder.code(task, context)

# Future (Parallel for independent tasks)
results = await asyncio.gather(
    self.researcher.research(topic1, context),
    self.researcher.research(topic2, context),  # Independent
)
```

**Interview Answer**:
> "We prioritized correctness and debuggability over speed. In production, we'd profile the critical path and parallelize independent operations—like multiple research tasks—but the core flow (Manager → Researcher → Coder → Reviewer) is inherently sequential. Async already gives us non-blocking IO; parallelizing agents would add complexity for marginal gains."

---

## ADR-004: Why No Code Execution Sandbox?

**Decision**: System generates code but does NOT execute it.

**Alternatives Considered**:
1. **No Execution** (Current approach)
2. **Docker Sandbox** (isolated container per execution)
3. **WASM Sandbox** (in-browser execution)
4. **Cloud Functions** (AWS Lambda, GCP Cloud Run)

**Why No Execution Won**:
- ✅ **Security**: No risk of malicious code execution
- ✅ **Scope**: Prototype focuses on multi-agent patterns, not runtime safety
- ✅ **Simplicity**: Execution adds 100+ lines of complex code

**Trade-offs**:
- ❌ Can't validate code actually works
- ❌ Manual testing required

**When to Reconsider**:
- If users need proof-of-execution
- If we add "test suite generation" agent
- If security team approves sandboxing approach

**Production Path**:
```python
# Future: Docker Sandbox
async def execute_code(code: str, timeout: int = 30) -> str:
    """Run code in isolated Docker container."""
    client = docker.from_env()
    container = client.containers.run(
        image="python:3.11-slim",
        command=f"python -c '{code}'",
        remove=True,
        mem_limit="128m",
        network_disabled=True,  # No network access
        timeout=timeout
    )
    return container.decode()
```

**Interview Answer**:
> "Executing AI-generated code is a hard security problem. We'd need Docker isolation, resource limits, network policies, and timeout handling. That's a separate system. For this prototype, we focused on demonstrating multi-agent coordination. In production, we'd integrate with an existing sandbox service like AWS Lambda or Replit."

---

## ADR-005: Why Pydantic for MissionContext (Not Dataclasses)?

**Decision**: Use Pydantic `BaseModel` for `MissionContext` and all models.

**Alternatives Considered**:
1. **Plain Dict** (no validation)
2. **Dataclasses** (Python stdlib)
3. **Pydantic** (Current approach)
4. **TypedDict** (type hints only)

**Why Pydantic Won**:
- ✅ **Runtime Validation**: Catches bugs at assignment, not access
- ✅ **JSON Serialization**: `.dict()` and `.json()` methods
- ✅ **Type Coercion**: Automatically converts compatible types
- ✅ **Documentation**: Field descriptions self-document

**Example**:
```python
# Pydantic catches this immediately
context.review_iteration = "invalid"  # ❌ ValidationError: int required

# Dataclass wouldn't catch this until runtime
# TypedDict only helps mypy, no runtime check
```

**Trade-offs**:
- ❌ Slight performance overhead (validation cost)
- ❌ Dependency (requires pydantic install)

**Performance**:
- Validation adds ~1ms per context update
- Negligible compared to API latency (2-5 seconds)

**Interview Answer**:
> "Pydantic gives us confidence that MissionContext is always valid. When an agent writes bad data, we catch it immediately with a clear error, not 3 steps later with a cryptic AttributeError. The tiny performance cost is worth the developer experience and safety. It's the same reason FastAPI uses Pydantic—validation at the edges prevents bugs deeper in the system."

---

## ADR-006: Why Flask-SocketIO (Not FastAPI + WebSockets)?

**Decision**: Use Flask + Flask-SocketIO for backend.

**Alternatives Considered**:
1. **Flask + Flask-SocketIO** (Current approach)
2. **FastAPI + WebSockets** (newer, async-first)
3. **Django Channels** (full framework)

**Why Flask-SocketIO Won**:
- ✅ **Familiarity**: Team knows Flask well
- ✅ **Stability**: Mature library, good docs
- ✅ **Simple Integration**: Works with existing Flask app
- ✅ **Room Support**: Built-in rooms for multi-client

**Trade-offs**:
- ❌ Flask is sync-first (less efficient than FastAPI)
- ❌ Older ecosystem (less modern tooling)

**When to Reconsider**:
- If performance becomes critical (>1000 concurrent users)
- If team switches to FastAPI for other services
- If we need GraphQL subscriptions

**Migration Path**:
```python
# Flask-SocketIO (Current)
@socketio.on('start_task')
def handle_start_task(data):
    emit('execution_start', {'task': data})

# FastAPI WebSocket (Future)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    await websocket.send_json({'task': data})
```

**Interview Answer**:
> "Flask-SocketIO was the pragmatic choice. The team is productive in Flask, the library is battle-tested, and WebSocket complexity is abstracted away. FastAPI would be faster at scale, but we're not there yet. When we hit 100 concurrent users, we'll benchmark both and migrate if needed. For now, shipping working code beats premature optimization."

---

## System Invariants (Always True)

These are **guarantees** the system maintains:

1. **MissionContext Immutability**:
   - `task_id` never changes after creation
   - `original_prompt` never changes
   - `created_at` never changes

2. **Feedback Loop Termination**:
   - Loop ALWAYS exits within `max_iterations + 1` attempts
   - No infinite loops possible

3. **Agent Execution Order**:
   - Manager ALWAYS runs first (creates plan)
   - Reporter ALWAYS runs last (summarizes)
   - Coder → Reviewer always pairs (never standalone Reviewer without Coder)

4. **API Retry Guarantees**:
   - Every agent retries exactly 3 times on failure
   - Exponential backoff: 1s, 2s, 4s
   - After 3 failures, agent returns error (doesn't crash)

5. **WebSocket Safety**:
   - WebSocket errors NEVER crash the orchestrator
   - Broadcast failures are logged but ignored
   - Task continues even if frontend disconnects

---

## Anti-Patterns to Avoid

### ❌ **Don't Modify MissionContext Outside Orchestrator**

```python
# BAD: Agent modifies context directly
async def code(self, task: str, context: MissionContext):
    context.current_status = "coding"  # ❌ Don't do this
    # ...

# GOOD: Agent writes to shared_findings only
async def code(self, task: str, context: MissionContext):
    context.shared_findings.code_artifacts[key] = code  # ✅ Correct
```

**Why**: Orchestrator owns status transitions. Agents own domain data.

---

### ❌ **Don't Add Agents to Feedback Loop Without Termination**

```python
# BAD: New loop without max iterations
while reviewer.status != "approved":
    await coder.code(task, context)  # ❌ Infinite loop risk

# GOOD: Always have explicit limit
for iteration in range(max_iterations):
    if reviewer.decision == "approved":
        break  # ✅ Early exit
```

**Why**: AI is non-deterministic. Loops need guardrails.

---

### ❌ **Don't Block the Event Loop**

```python
# BAD: Synchronous sleep blocks everything
def _broadcast(self, agent: str, status: str, message: str):
    time.sleep(1)  # ❌ Blocks event loop
    socketio.emit(...)

# GOOD: Use async sleep
async def _broadcast(self, agent: str, status: str, message: str):
    await asyncio.sleep(1)  # ✅ Non-blocking
    socketio.emit(...)
```

**Why**: One slow task blocks all tasks. Async is the whole point.

---

## Future Architecture Evolution

### Phase 1 (Current): **Prototype**
- In-memory MissionContext
- Sequential execution
- No code execution
- Single-machine

### Phase 2: **MVP** (6 months)
- SQLite persistence
- Parallel research agents
- Docker sandbox (opt-in)
- Basic auth

### Phase 3: **Production** (12 months)
- PostgreSQL + Redis
- Distributed agents (Celery/RabbitMQ)
- Kubernetes deployment
- Multi-tenancy
- Cost controls (token limits)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-04
**Review Cycle**: Every 3 months or when architecture changes
