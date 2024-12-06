import pytest
from src.gerencia_ccr.web.app import create_app
from pymongo import MongoClient
import os
from dotenv import load_dotenv

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    load_dotenv()
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def mongo_client():
    """Create a MongoDB test client."""
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    return client
