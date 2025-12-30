#!/usr/bin/env python3
"""
Multi-Agent System - Flask Web Application with WebSockets
"""
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from orchestrator import MultiAgentOrchestrator

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize orchestrator
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        orchestrator = MultiAgentOrchestrator(api_key=api_key)
    return orchestrator


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def status():
    """Get system and agent status."""
    try:
        orch = get_orchestrator()
        return jsonify({
            'status': 'online',
            'agents': orch.get_agent_status(),
            'anthropic_key_set': bool(os.getenv('ANTHROPIC_API_KEY'))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute', methods=['POST'])
def execute_task():
    """
    Execute a task with the multi-agent system.

    Request body:
    {
        "task": "User's complex task"
    }
    """
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({'error': 'Missing task in request'}), 400

        user_task = data['task']

        orch = get_orchestrator()
        result = orch.execute_task(user_task)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get information about all available agents."""
    try:
        orch = get_orchestrator()
        return jsonify({
            'agents': [
                {
                    'name': 'Manager',
                    'role': 'Task Coordinator & Delegation',
                    'emoji': '🎯',
                    'description': 'Analyzes complex tasks and coordinates the team'
                },
                {
                    'name': 'Researcher',
                    'role': 'Information Gathering & Analysis',
                    'emoji': '🔍',
                    'description': 'Researches and analyzes information'
                },
                {
                    'name': 'Coder',
                    'role': 'Code Implementation & Development',
                    'emoji': '💻',
                    'description': 'Writes clean, efficient code'
                },
                {
                    'name': 'Reviewer',
                    'role': 'Quality Assurance & Code Review',
                    'emoji': '✅',
                    'description': 'Reviews code and ensures quality'
                },
                {
                    'name': 'Reporter',
                    'role': 'Documentation & Reporting',
                    'emoji': '📊',
                    'description': 'Creates documentation and summaries'
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset all agents' conversation history."""
    try:
        orch = get_orchestrator()
        orch.reset_all_agents()
        return jsonify({'status': 'reset', 'message': 'All agents reset successfully'})
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


@socketio.on('execute_realtime')
def handle_realtime_execution(data):
    """Execute task with real-time updates via WebSocket."""
    try:
        user_task = data.get('task', '')
        if not user_task:
            emit('error', {'message': 'No task provided'})
            return

        # Get orchestrator
        orch = get_orchestrator()

        # Emit start event
        emit('execution_start', {'task': user_task})

        # Execute with custom callback for real-time updates
        def emit_progress(agent, status, message):
            socketio.emit('agent_update', {
                'agent': agent,
                'status': status,
                'message': message
            })

        # Monkey-patch the orchestrator's log function for this execution
        original_log = orch._log
        def realtime_log(agent, status, message):
            original_log(agent, status, message)
            emit_progress(agent, status, message)

        orch._log = realtime_log

        try:
            # Execute the task
            result = orch.execute_task(user_task)

            # Emit completion
            emit('execution_complete', {
                'result': result,
                'final_report': result.get('final_report', '')
            })

        finally:
            # Restore original log function
            orch._log = original_log

    except Exception as e:
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"""
    ╔══════════════════════════════════════════╗
    ║   🤖 Multi-Agent System Starting...     ║
    ║   ⚡ WebSockets Enabled!                ║
    ╚══════════════════════════════════════════╝

    📍 Server: http://localhost:{port}
    🔑 API Key: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Not Set'}
    🎯 Agents: Manager, Researcher, Coder, Reviewer, Reporter
    ⚡ Real-time: WebSockets streaming enabled

    """)

    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
