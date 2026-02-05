#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous Claude - Web Interface
ממשק Web מלא עם Dashboard אינטראקטיבי
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_compress import Compress
import os
import sys
import json
from datetime import datetime
import threading
import time
from functools import wraps
from logging_config import setup_logging

# Initialize logger
logger = setup_logging('web_app')

# Add autonomous-claude to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import short_term, long_term
from claude_brain import ClaudeBrain, AutonomousAgentWithClaude

app = Flask(__name__)
CORS(app)
Compress(app)  # Enable Gzip compression - reduces file sizes by 70%+

# Configure compression
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml',
    'application/json', 'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6  # Balance between speed and compression
app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress files > 500 bytes

# Simple cache for performance
cache = {
    'stats': {'data': None, 'timestamp': 0},
    'memories': {'data': None, 'timestamp': 0}
}
CACHE_TTL = 5  # Cache for 5 seconds

# Global agent state with thread safety
agent_state = {
    'running': False,
    'current_goal': None,
    'iteration': 0,
    'last_decision': None,
    'agent': None,
    'brain': None
}
agent_state_lock = threading.Lock()  # Thread-safe access to agent_state

# Authentication decorator for sensitive endpoints
def require_api_key(f):
    """Decorator to require API key authentication for sensitive operations."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = os.getenv('API_SECRET_KEY')

        # If no API key is configured, allow access (development mode)
        if not expected_key:
            return f(*args, **kwargs)

        # Check if provided key matches
        if api_key != expected_key:
            return jsonify({'error': 'Unauthorized. Valid API key required.'}), 401

        return f(*args, **kwargs)
    return decorated_function

# Input validation helpers
def validate_string(value, field_name, min_length=1, max_length=10000):
    """Validate string input."""
    if not isinstance(value, str):
        return f"{field_name} must be a string"
    if len(value) < min_length:
        return f"{field_name} must be at least {min_length} characters"
    if len(value) > max_length:
        return f"{field_name} must be at most {max_length} characters"
    return None

def validate_memory_type(memory_type):
    """Validate memory type."""
    valid_types = ['action', 'observation', 'thought', 'goal']
    if memory_type not in valid_types:
        return f"Invalid memory type. Must be one of: {', '.join(valid_types)}"
    return None

def initialize_brain():
    """Initialize Claude Brain if API key is available."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    with agent_state_lock:
        if api_key and not agent_state['brain']:
            try:
                agent_state['brain'] = ClaudeBrain(api_key=api_key, model="claude-opus-4-5-20251101")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Claude Brain: {e}")
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


@app.route('/showcase')
def showcase():
    """Showcase page - what we built."""
    return render_template('showcase.html')


@app.route('/api/status')
def get_status():
    """Get current agent status."""
    with agent_state_lock:
        return jsonify({
            'running': agent_state['running'],
            'current_goal': agent_state['current_goal'],
            'iteration': agent_state['iteration'],
            'last_decision': agent_state['last_decision'],
            'brain_available': agent_state['brain'] is not None,
            'anthropic_key_set': os.getenv('ANTHROPIC_API_KEY') is not None,
            'qdrant_available': long_term.qdrant_available
        })


@app.route('/api/memories/recent')
def get_recent_memories():
    """Get recent memories from short-term storage with pagination support."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Validate pagination parameters
    if limit < 1 or limit > 100:
        return jsonify({'error': 'Limit must be between 1 and 100'}), 400
    if offset < 0:
        return jsonify({'error': 'Offset must be non-negative'}), 400

    # Fetch memories (get more than needed to apply offset)
    memories = short_term.get_recent(limit + offset)

    # Apply pagination
    paginated_memories = memories[offset:offset + limit]

    # Format for JSON
    formatted = []
    for m in paginated_memories:
        formatted.append({
            'id': m['id'],
            'type': m['type'],
            'content': m['content'],
            'timestamp': m['timestamp'].isoformat() if hasattr(m['timestamp'], 'isoformat') else str(m['timestamp'])
        })

    return jsonify({
        'data': formatted,
        'pagination': {
            'limit': limit,
            'offset': offset,
            'count': len(formatted),
            'has_more': len(formatted) == limit
        }
    })


@app.route('/api/memories/search')
def search_memories():
    """Search memories by type."""
    memory_type = request.args.get('type')
    if not memory_type:
        return jsonify({'error': 'Type parameter required'}), 400

    # Validate memory type
    type_error = validate_memory_type(memory_type)
    if type_error:
        return jsonify({'error': type_error}), 400

    # Get pagination parameters
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Validate pagination parameters
    if limit < 1 or limit > 100:
        return jsonify({'error': 'Limit must be between 1 and 100'}), 400
    if offset < 0:
        return jsonify({'error': 'Offset must be non-negative'}), 400

    # Fetch memories
    memories = short_term.get_by_type(memory_type, limit=limit + offset)

    # Apply pagination
    paginated_memories = memories[offset:offset + limit]

    formatted = []
    for m in paginated_memories:
        formatted.append({
            'id': m['id'],
            'type': m['type'],
            'content': m['content'],
            'timestamp': m['timestamp'].isoformat() if hasattr(m['timestamp'], 'isoformat') else str(m['timestamp'])
        })

    return jsonify({
        'data': formatted,
        'pagination': {
            'limit': limit,
            'offset': offset,
            'count': len(formatted),
            'has_more': len(formatted) == limit
        }
    })


@app.route('/api/memories/stats')
def get_memory_stats():
    """Get memory statistics with caching for better performance."""
    # Check cache
    current_time = time.time()
    if cache['stats']['data'] and current_time - cache['stats']['timestamp'] < CACHE_TTL:
        return jsonify(cache['stats']['data'])

    # Reduced from 1000 to 200 for better performance
    recent = short_term.get_recent(200)

    type_counts = {}
    for m in recent:
        t = m['type']
        type_counts[t] = type_counts.get(t, 0) + 1

    result = {
        'total': len(recent),
        'by_type': type_counts
    }

    # Update cache
    cache['stats'] = {'data': result, 'timestamp': current_time}

    return jsonify(result)


@app.route('/api/memories/add', methods=['POST'])
def add_memory():
    """Add a new memory."""
    data = request.json
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    # Validate required fields
    if 'type' not in data:
        return jsonify({'error': 'Field "type" is required'}), 400
    if 'content' not in data:
        return jsonify({'error': 'Field "content" is required'}), 400

    # Validate memory type
    type_error = validate_memory_type(data['type'])
    if type_error:
        return jsonify({'error': type_error}), 400

    # Validate content
    content_error = validate_string(data['content'], 'content', min_length=1, max_length=5000)
    if content_error:
        return jsonify({'error': content_error}), 400

    try:
        memory_id = short_term.add(data['type'], data['content'])
        return jsonify({'success': True, 'id': memory_id})
    except Exception as e:
        return jsonify({'error': f'Failed to add memory: {str(e)}'}), 500


@app.route('/api/agent/goal', methods=['POST'])
def set_goal():
    """Set agent goal."""
    data = request.json
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    if 'goal' not in data:
        return jsonify({'error': 'Field "goal" is required'}), 400

    # Validate goal
    goal_error = validate_string(data['goal'], 'goal', min_length=3, max_length=1000)
    if goal_error:
        return jsonify({'error': goal_error}), 400

    with agent_state_lock:
        agent_state['current_goal'] = data['goal']
    short_term.add('goal', data['goal'])

    return jsonify({'success': True, 'goal': data['goal']})


@app.route('/api/agent/start', methods=['POST'])
@require_api_key
def start_agent():
    """Start the autonomous agent."""
    with agent_state_lock:
        if agent_state['running']:
            return jsonify({'error': 'Agent already running'}), 400

        if not agent_state['current_goal']:
            return jsonify({'error': 'No goal set'}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'Claude Brain not available. Set ANTHROPIC_API_KEY.'}), 500

    with agent_state_lock:
        agent_state['running'] = True
        agent_state['iteration'] = 0
        current_goal = agent_state['current_goal']

    # Start agent in background thread
    def run_agent():
        try:
            agent = AutonomousAgentWithClaude(model="claude-opus-4-5-20251101")
            agent.set_goal(current_goal)

            with agent_state_lock:
                agent_state['agent'] = agent

            while True:
                with agent_state_lock:
                    if not agent_state['running']:
                        break

                agent.run_cycle()

                with agent_state_lock:
                    agent_state['iteration'] = agent.iteration

                time.sleep(2)  # Delay between cycles

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            with agent_state_lock:
                agent_state['running'] = False

    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()

    return jsonify({'success': True})


@app.route('/api/agent/stop', methods=['POST'])
@require_api_key
def stop_agent():
    """Stop the autonomous agent."""
    with agent_state_lock:
        agent_state['running'] = False
        agent_state['agent'] = None

    return jsonify({'success': True})


@app.route('/api/claude/think', methods=['POST'])
def claude_think():
    """Ask Claude to think about a situation."""
    data = request.json
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    if 'situation' not in data:
        return jsonify({'error': 'Field "situation" is required'}), 400

    # Validate situation
    situation_error = validate_string(data['situation'], 'situation', min_length=3, max_length=5000)
    if situation_error:
        return jsonify({'error': situation_error}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'Claude Brain not available. Set ANTHROPIC_API_KEY.'}), 500

    try:
        with agent_state_lock:
            brain = agent_state['brain']

        context = data.get('context', {})
        decision = brain.think(data['situation'], context)

        with agent_state_lock:
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


@app.route('/api/claude/analyze', methods=['POST'])
def claude_analyze():
    """Ask Claude to analyze and decide."""
    data = request.json
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    if 'goal' not in data:
        return jsonify({'error': 'Field "goal" is required'}), 400
    if 'observations' not in data:
        return jsonify({'error': 'Field "observations" is required'}), 400

    # Validate goal
    goal_error = validate_string(data['goal'], 'goal', min_length=3, max_length=1000)
    if goal_error:
        return jsonify({'error': goal_error}), 400

    # Validate observations (can be string or list)
    if isinstance(data['observations'], str):
        obs_error = validate_string(data['observations'], 'observations', min_length=1, max_length=10000)
        if obs_error:
            return jsonify({'error': obs_error}), 400
    elif not isinstance(data['observations'], list):
        return jsonify({'error': 'observations must be a string or list'}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'Claude Brain not available. Set ANTHROPIC_API_KEY.'}), 500

    try:
        with agent_state_lock:
            brain = agent_state['brain']

        analysis = brain.analyze_and_decide(
            data['goal'],
            data['observations']
        )

        with agent_state_lock:
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


@app.route('/api/claude/learn', methods=['POST'])
def claude_learn():
    """Ask Claude to learn from experience."""
    data = request.json
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    if 'experience' not in data:
        return jsonify({'error': 'Field "experience" is required'}), 400
    if 'outcome' not in data:
        return jsonify({'error': 'Field "outcome" is required'}), 400

    # Validate experience
    exp_error = validate_string(data['experience'], 'experience', min_length=3, max_length=5000)
    if exp_error:
        return jsonify({'error': exp_error}), 400

    # Validate outcome
    outcome_error = validate_string(data['outcome'], 'outcome', min_length=3, max_length=5000)
    if outcome_error:
        return jsonify({'error': outcome_error}), 400

    # Initialize brain if needed
    if not initialize_brain():
        return jsonify({'error': 'Claude Brain not available. Set ANTHROPIC_API_KEY.'}), 500

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
@require_api_key
def clear_database():
    """Clear all memories (use with caution!). Requires API key authentication."""
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


@app.route('/api/figma/import', methods=['POST'])
def import_figma():
    """Import design from Figma."""
    data = request.json
    if not data or 'file_key' not in data:
        return jsonify({'error': 'Figma file_key required'}), 400

    try:
        from figma_integration import FigmaClient

        # Get token from env or request
        token = data.get('token') or os.getenv('FIGMA_TOKEN')
        if not token:
            return jsonify({'error': 'FIGMA_TOKEN not set'}), 400

        client = FigmaClient(token=token)
        file_data = client.get_file(data['file_key'])

        # Extract design data
        colors = client.extract_colors(file_data)
        text_styles = client.extract_text_styles(file_data)
        components = client.extract_components(file_data)

        # Generate code
        tailwind_config = client.generate_tailwind_config(file_data)
        css_variables = client.generate_css_variables(file_data)

        return jsonify({
            'success': True,
            'file_name': file_data.get('name'),
            'colors': colors[:10],
            'text_styles': text_styles[:10],
            'components': len(components),
            'tailwind_config': tailwind_config,
            'css_variables': css_variables
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🤖 Autonomous Claude - Web Interface")
    logger.info("=" * 70)

    # Check API key
    if os.getenv('ANTHROPIC_API_KEY'):
        logger.info("✅ ANTHROPIC_API_KEY found")
        initialize_brain()
    else:
        logger.warning("⚠️  ANTHROPIC_API_KEY not set - Claude features will be unavailable")
        logger.info("   Set it with: export ANTHROPIC_API_KEY='your-key'")

    logger.info("🌐 Starting web server...")

    # Get port from environment (for Railway, Heroku, etc.)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    # Run server
    app.run(host='0.0.0.0', port=port, debug=debug)
