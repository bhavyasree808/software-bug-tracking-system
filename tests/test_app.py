
import sqlite3
import tempfile
from pathlib import Path

import pytest
import app as bug_app


@pytest.fixture
def client(monkeypatch):
    # Use a temporary directory for each test database.
    temp_dir = tempfile.TemporaryDirectory()
    db_path = Path(temp_dir.name) / "test_bugs.db"

    monkeypatch.setattr(bug_app, "DB_PATH", db_path)
    bug_app.app.config.update(TESTING=True)

    with bug_app.app.test_client() as test_client:
        yield test_client

    # Ensure all connections are closed before cleanup.
    # The application's database operations use context managers.
    temp_dir.cleanup()


def create_bug(
    client,
    title="Login button broken",
    description="Clicking login does nothing",
    severity="High",
):
    return client.post(
        "/bugs",
        data={
            "title": title,
            "description": description,
            "severity": severity,
            "assigned_to": "Developer A",
        },
        follow_redirects=True,
    )


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"BugTrack" in response.data


def test_create_bug(client):
    response = create_bug(client)
    assert response.status_code == 200
    assert b"Login button broken" in response.data


def test_reject_empty_bug(client):
    response = client.post(
        "/bugs",
        data={"title": "", "description": "", "severity": "High"},
        follow_redirects=True,
    )
    assert b"Enter a title and description" in response.data


def test_search_bug(client):
    create_bug(client, title="Searchable checkout error")
    response = client.get("/?q=checkout")
    assert b"Searchable checkout error" in response.data
    assert b"Login button broken" not in response.data


def test_update_status(client):
    create_bug(client)
    response = client.post(
        "/bugs/1/update",
        data={"status": "Resolved", "assigned_to": "Developer B"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Resolved" in response.data
    assert b"Developer B" in response.data


def test_reject_invalid_status(client):
    create_bug(client)
    response = client.post(
        "/bugs/1/update",
        data={"status": "Invalid", "assigned_to": ""},
        follow_redirects=True,
    )
    assert b"Invalid status selected" in response.data


def test_delete_bug(client):
    create_bug(client)
    response = client.post("/bugs/1/delete", follow_redirects=True)
    assert b"Login button broken" not in response.data
