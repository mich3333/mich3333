#!/usr/bin/env python3
"""
Multi-Agent System - Flask Web Application with Async WebSockets
"""
import asyncio
import os
from threading import Thread

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from orchestrator import MultiAgentOrchestrator

# Load environment variables from .env file
load_dotenv()

# Custom middleware to bypass host checking
class TrustedHostMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Allow any host
        return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = TrustedHostMiddleware(app.wsgi_app)
CORS(app)
# Configure SocketIO with threading
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    engineio_logger=False,
    logger=False
)

# Global orchestrator instance
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        # Create websocket callback (thread-safe with SocketIO)
        def websocket_broadcast(agent: str, status: str, message: str):
            """
            Broadcast agent updates to all connected clients.
            Thread-safe: SocketIO handles cross-thread communication automatically.
            """
            try:
                socketio.emit('agent_update', {
                    'agent': agent,
                    'status': status,
                    'message': message
                }, namespace='/')
            except Exception as e:
                print(f"⚠️  Broadcast error: {e}")

        orchestrator = MultiAgentOrchestrator(
            api_key=api_key,
            websocket_callback=websocket_broadcast
        )
    return orchestrator


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Docker."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/status', methods=['GET'])
def status():
    """Get system and agent status."""
    try:
        orch = get_orchestrator()
        return jsonify({
            'status': 'online',
            'agents': orch.get_agent_status(),
            'active_tasks': orch.get_active_tasks(),
            'anthropic_key_set': bool(os.getenv('ANTHROPIC_API_KEY'))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get information about all available agents."""
    try:
        return jsonify({
            'agents': [
                {
                    'name': 'Manager',
                    'role': 'Task Coordinator & Delegation',
                    'emoji': '🎯',
                    'description': 'Analyzes tasks and creates JSON execution plans'
                },
                {
                    'name': 'Researcher',
                    'role': 'Information Gathering & Analysis',
                    'emoji': '🔍',
                    'description': 'Researches and writes findings to shared memory'
                },
                {
                    'name': 'Coder',
                    'role': 'Code Implementation & Development',
                    'emoji': '💻',
                    'description': 'Writes code with retry logic based on review feedback'
                },
                {
                    'name': 'Reviewer',
                    'role': 'Quality Assurance & Code Review',
                    'emoji': '✅',
                    'description': 'Reviews code and provides APPROVED/REJECTED/NEEDS_REVISION decisions'
                },
                {
                    'name': 'Reporter',
                    'role': 'Documentation & Reporting',
                    'emoji': '📊',
                    'description': 'Creates final documentation from shared context'
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket events for real-time streaming
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('🔌 Client connected')
    emit('status', {'message': 'Connected to Multi-Agent System'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('🔌 Client disconnected')


@socketio.on('start_task')
def handle_start_task(data):
    """
    Start a new task execution (async in background thread).

    Expected data:
    {
        "task": "User's task description"
    }
    """
    try:
        user_task = data.get('task', '')
        if not user_task:
            emit('error', {'message': 'No task provided'})
            return

        # Get orchestrator
        orch = get_orchestrator()

        # Emit start event
        emit('execution_start', {
            'task': user_task,
            'message': 'Task execution started'
        })

        # Run async task in background thread
        def run_async_task():
            """Run the async task in a separate thread with its own event loop."""
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # Execute the task (async)
                    result = loop.run_until_complete(orch.execute_task(user_task))

                    # Emit completion (thread-safe with socketio)
                    socketio.emit('execution_complete', {
                        'result': result,
                        'task_id': result.get('task_id'),
                        'status': result.get('status'),
                        'final_report': result.get('final_report', '')
                    })

                except Exception as e:
                    socketio.emit('error', {'message': f'Task execution failed: {str(e)}'})

                finally:
                    loop.close()

            except Exception as e:
                socketio.emit('error', {'message': f'Thread execution failed: {str(e)}'})

        # Start background thread
        thread = Thread(target=run_async_task, daemon=True)
        thread.start()

    except Exception as e:
        emit('error', {'message': f'Task start failed: {str(e)}'})


@socketio.on('cancel_task')
def handle_cancel_task(data):
    """
    Cancel an active task.

    Expected data:
    {
        "task_id": "task_id_to_cancel"
    }
    """
    try:
        task_id = data.get('task_id', '')
        if not task_id:
            emit('error', {'message': 'No task_id provided'})
            return

        # Get orchestrator
        orch = get_orchestrator()

        # Cancel the task
        orch.cancel_task(task_id)

        emit('task_cancelled', {
            'task_id': task_id,
            'message': f'Task {task_id} cancellation requested'
        })

    except Exception as e:
        emit('error', {'message': f'Task cancellation failed: {str(e)}'})


@socketio.on('get_active_tasks')
def handle_get_active_tasks():
    """Get list of currently active tasks."""
    try:
        orch = get_orchestrator()
        active_tasks = orch.get_active_tasks()

        emit('active_tasks', {
            'tasks': active_tasks,
            'count': len(active_tasks)
        })

    except Exception as e:
        emit('error', {'message': f'Failed to get active tasks: {str(e)}'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"""
    ╔══════════════════════════════════════════╗
    ║   🤖 Multi-Agent System v2.0            ║
    ║   ⚡ Async + Feedback Loops Enabled!   ║
    ╚══════════════════════════════════════════╝

    📍 Server: http://localhost:{port}
    📱 Mobile Access: http://21.0.0.128:{port}
    🔑 API Key: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Not Set'}
    🎯 Agents: Manager, Researcher, Coder, Reviewer, Reporter
    ⚡ Real-time: WebSockets with async execution
    🔄 Feedback Loop: Reviewer → Coder retry logic
    🎨 Shared State: MissionContext with audit trail

    WebSocket Events:
    - start_task: Execute a new task
    - cancel_task: Cancel running task
    - get_active_tasks: List active tasks
    - agent_update: Real-time agent thoughts (emitted)

    """)

    #  Patch Werkzeug's trusted hosts check
    from werkzeug import serving
    serving.WSGIRequestHandler.server_version = "MultiAgent/2.0"

    # Monkey-patch to disable host validation
    def no_host_validation(self, *args, **kwargs):
        pass
    serving.BaseWSGIServer._validate_server_name = no_host_validation

    print(f"🚀 Starting server on 0.0.0.0:{port} (all network interfaces)...")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True, use_reloader=False)
