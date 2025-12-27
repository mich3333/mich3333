#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous Claude - Web Interface
ממשק Web מלא עם Dashboard אינטראקטיבי
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import threading
import time

# Add autonomous-claude to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import short_term, long_term
from chatgpt_brain import ChatGPTBrain, AutonomousAgentWithChatGPT

app = Flask(__name__)
CORS(app)

# Global agent state
agent_state = {
    'running': False,
    'current_goal': None,
    'iteration': 0,
    'last_decision': None,
    'agent': None,
    'brain': None
}

def initialize_brain():
    """Initialize ChatGPT Brain if API key is available."""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and not agent_state['brain']:
        try:
            agent_state['brain'] = ChatGPTBrain(api_key=api_key, model="gpt-3.5-turbo")
            return True
        except Exception as e:
            print(f"Failed to initialize ChatGPT Brain: {e}")
            return False
    return agent_state['brain'] is not None


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Portfolio landing page."""
    return render_template('portfolio.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current agent status."""
    return jsonify({
        'running': agent_state['running'],
        'current_goal': agent_state['current_goal'],
        'iteration': agent_state['iteration'],
        'last_decision': agent_state['last_decision'],
        'brain_available': agent_state['brain'] is not None,
        'openai_key_set': os.getenv('OPENAI_API_KEY') is not None,
        'qdrant_available': long_term.qdrant_available
    })


@app.route('/api/memories/recent')
def get_recent_memories():
    """Get recent memories from short-term storage."""
    limit = request.args.get('limit', 50, type=int)
    memories = short_term.get_recent(limit)

    # Format for JSON
    formatted = []
    for m in memories:
        formatted.append({
            'id': m['id'],
            'type': m['type'],
            'content': m['content'],
            'timestamp': m['timestamp'].isoformat() if hasattr(m['timestamp'], 'isoformat') else str(m['timestamp'])
        })

    return jsonify(formatted)


@app.route('/api/memories/search')
def search_memories():
    """Search memories by type."""
    memory_type = request.args.get('type')
    if not memory_type:
        return jsonify({'error': 'Type parameter required'}), 400

    memories = short_term.get_by_type(memory_type, limit=50)

    formatted = []
    for m in memories:
        formatted.append({
            'id': m['id'],
            'type': m['type'],
            'content': m['content'],
            'timestamp': m['timestamp'].isoformat() if hasattr(m['timestamp'], 'isoformat') else str(m['timestamp'])
        })

    return jsonify(formatted)


@app.route('/api/memories/stats')
def get_memory_stats():
    """Get memory statistics."""
    recent = short_term.get_recent(1000)

    type_counts = {}
    for m in recent:
        t = m['type']
        type_counts[t] = type_counts.get(t, 0) + 1

    return jsonify({
        'total': len(recent),
        'by_type': type_counts
    })


@app.route('/api/memories/add', methods=['POST'])
def add_memory():
    """Add a new memory."""
    data = request.json
    if not data or 'type' not in data or 'content' not in data:
        return jsonify({'error': 'Type and content required'}), 400

    try:
        memory_id = short_term.add(data['type'], data['content'])
        return jsonify({'success': True, 'id': memory_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agent/goal', methods=['POST'])
def set_goal():
    """Set agent goal."""
    data = request.json
    if not data or 'goal' not in data:
        return jsonify({'error': 'Goal required'}), 400

    agent_state['current_goal'] = data['goal']
    short_term.add('goal', data['goal'])

    return jsonify({'success': True, 'goal': data['goal']})


@app.route('/api/agent/start', methods=['POST'])
def start_agent():
    """Start the autonomous agent."""
    if agent_state['running']:
        return jsonify({'error': 'Agent already running'}), 400

    if not agent_state['current_goal']:
        return jsonify({'error': 'No goal set'}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'ChatGPT Brain not available. Set OPENAI_API_KEY.'}), 500

    agent_state['running'] = True
    agent_state['iteration'] = 0

    # Start agent in background thread
    def run_agent():
        try:
            agent = AutonomousAgentWithChatGPT(model="gpt-3.5-turbo")
            agent.set_goal(agent_state['current_goal'])
            agent_state['agent'] = agent

            while agent_state['running']:
                agent.run_cycle()
                agent_state['iteration'] = agent.iteration
                time.sleep(2)  # Delay between cycles

        except Exception as e:
            print(f"Agent error: {e}")
            agent_state['running'] = False

    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()

    return jsonify({'success': True})


@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
    """Stop the autonomous agent."""
    agent_state['running'] = False
    agent_state['agent'] = None

    return jsonify({'success': True})


@app.route('/api/chatgpt/think', methods=['POST'])
def chatgpt_think():
    """Ask ChatGPT to think about a situation."""
    data = request.json
    if not data or 'situation' not in data:
        return jsonify({'error': 'Situation required'}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'ChatGPT Brain not available. Set OPENAI_API_KEY.'}), 500

    try:
        context = data.get('context', {})
        decision = agent_state['brain'].think(data['situation'], context)

        agent_state['last_decision'] = {
            'situation': data['situation'],
            'decision': decision,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'decision': decision
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chatgpt/analyze', methods=['POST'])
def chatgpt_analyze():
    """Ask ChatGPT to analyze and decide."""
    data = request.json
    if not data or 'goal' not in data or 'observations' not in data:
        return jsonify({'error': 'Goal and observations required'}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'ChatGPT Brain not available. Set OPENAI_API_KEY.'}), 500

    try:
        analysis = agent_state['brain'].analyze_and_decide(
            data['goal'],
            data['observations']
        )

        agent_state['last_decision'] = {
            'goal': data['goal'],
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chatgpt/learn', methods=['POST'])
def chatgpt_learn():
    """Ask ChatGPT to learn from experience."""
    data = request.json
    if not data or 'experience' not in data or 'outcome' not in data:
        return jsonify({'error': 'Experience and outcome required'}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'ChatGPT Brain not available. Set OPENAI_API_KEY.'}), 500

    try:
        lesson = agent_state['brain'].learn_from_experience(
            data['experience'],
            data['outcome']
        )

        return jsonify({
            'success': True,
            'lesson': lesson
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/database/clear', methods=['POST'])
def clear_database():
    """Clear all memories (use with caution!)."""
    try:
        import sqlite3
        conn = sqlite3.connect(short_term.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'All memories cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("🤖 Autonomous Claude - Web Interface")
    print("=" * 70)
    print()

    # Check API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY found")
        initialize_brain()
    else:
        print("⚠️  OPENAI_API_KEY not set - ChatGPT features will be unavailable")
        print("   Set it with: export OPENAI_API_KEY='your-key'")

    print()
    print(f"🌐 Starting web server...")
    print()

    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
