"""Pytest configuration and fixtures for F1 Race Intelligence tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal


@pytest.fixture(scope="session")
def client():
    """Test client for FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def db_session():
    """Database session fixture."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
