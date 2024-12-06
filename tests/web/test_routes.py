"""
Tests for web routes
"""
import pytest
import os
from flask import url_for

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setenv('JWT_SECRET_KEY', 'test-jwt-key')

def test_index_route(client):
    """Test the index route returns the main page."""
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard_route(client):
    """Test the dashboard route returns the dashboard page."""
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_static_route(client):
    """Test static files are served correctly."""
    response = client.get('/static/index.html')
    assert response.status_code == 200
