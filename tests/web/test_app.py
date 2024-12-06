"""
Tests for the Flask application configuration
"""
import pytest
import os
from src.gerencia_ccr.web.app import create_app

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setenv('JWT_SECRET_KEY', 'test-jwt-key')

def test_app_creation():
    """Test application factory."""
    app = create_app()
    assert app.debug is True

def test_cors_configuration():
    """Test CORS is properly configured."""
    app = create_app()
    assert 'CORS_HEADERS' in app.config

def test_jwt_configuration():
    """Test JWT is properly configured."""
    app = create_app()
    assert 'JWT_SECRET_KEY' in app.config
    assert app.config['JWT_SECRET_KEY'] == 'test-jwt-key'

def test_static_path_configuration():
    """Test static path configuration."""
    app = create_app()
    assert app.static_url_path == ''
    assert app.static_folder.endswith('static')
