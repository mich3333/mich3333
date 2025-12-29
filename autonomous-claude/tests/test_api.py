"""
Unit Tests for Autonomous Claude Web API
"""
import pytest
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web_app import app


class TestAPI:
    """Test suite for Flask API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_index_route(self, client):
        """Test portfolio landing page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Autonomous Claude' in response.data

    def test_dashboard_route(self, client):
        """Test dashboard route."""
        response = client.get('/dashboard')
        assert response.status_code == 200

    def test_showcase_route(self, client):
        """Test showcase route."""
        response = client.get('/showcase')
        assert response.status_code == 200
        assert b'Showcase' in response.data

    def test_status_endpoint(self, client):
        """Test status API endpoint."""
        response = client.get('/api/status')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'running' in data
        assert 'iteration' in data
        assert 'brain_available' in data
        assert isinstance(data['running'], bool)
        assert isinstance(data['iteration'], int)

    def test_recent_memories_endpoint(self, client):
        """Test recent memories endpoint."""
        response = client.get('/api/memories/recent')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_memory_stats_endpoint(self, client):
        """Test memory stats endpoint."""
        response = client.get('/api/memories/stats')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'total' in data
        assert isinstance(data['total'], int)

    def test_add_memory_endpoint(self, client):
        """Test adding memory via API."""
        response = client.post('/api/memories/add',
                               json={'type': 'thought', 'content': 'Test thought'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'id' in data

    def test_add_memory_missing_fields(self, client):
        """Test adding memory with missing fields."""
        response = client.post('/api/memories/add',
                               json={'type': 'thought'},
                               content_type='application/json')

        assert response.status_code == 400

    def test_set_goal_endpoint(self, client):
        """Test setting agent goal."""
        response = client.post('/api/agent/goal',
                               json={'goal': 'Test goal'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_set_goal_missing_field(self, client):
        """Test setting goal without goal field."""
        response = client.post('/api/agent/goal',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get('/api/status')
        # CORS middleware should add headers
        assert response.status_code == 200


class TestFigmaAPI:
    """Test suite for Figma integration endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_figma_import_missing_key(self, client):
        """Test Figma import without file key."""
        response = client.post('/api/figma/import',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_figma_import_missing_token(self, client):
        """Test Figma import without token."""
        response = client.post('/api/figma/import',
                               json={'file_key': 'test123'},
                               content_type='application/json')

        # Should fail if no FIGMA_TOKEN env var
        assert response.status_code in [400, 500]


class TestErrorHandling:
    """Test error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_404_error(self, client):
        """Test 404 on non-existent route."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test invalid JSON handling."""
        response = client.post('/api/memories/add',
                               data='invalid json',
                               content_type='application/json')

        assert response.status_code in [400, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
