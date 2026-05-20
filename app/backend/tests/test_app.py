import pytest
from app import app, db, Note

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        db.drop_all()

def test_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200
    assert rv.get_json() == {"status": "ok"}

def test_create_note(client):
    rv = client.post('/api/notes', json={
        "title": "Test Note",
        "body": "This is a test note."
    })
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["message"] == "Note created"
    assert "id" in data

def test_create_note_missing_fields(client):
    rv = client.post('/api/notes', json={"title": "Only title"})
    assert rv.status_code == 400
    assert "error" in rv.get_json()

def test_get_notes(client):
    client.post('/api/notes', json={
        "title": "Note 1",
        "body": "Body 1"
    })
    rv = client.get('/api/notes')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Note 1"
    assert "created_at" in data[0]

def test_get_notes_search(client):
    client.post('/api/notes', json={"title": "Apple", "body": "Fruit"})
    client.post('/api/notes', json={"title": "Banana", "body": "Also fruit"})
    rv = client.get('/api/notes?search=apple')
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Apple"

def test_update_note(client):
    rv_create = client.post('/api/notes', json={
        "title": "Original",
        "body": "Original body"
    })
    note_id = rv_create.get_json()["id"]
    
    rv_update = client.put(f'/api/notes/{note_id}', json={
        "title": "Updated Title",
        "body": "Updated body"
    })
    assert rv_update.status_code == 200
    assert rv_update.get_json()["message"] == "Note updated"
    
    rv_get = client.get('/api/notes')
    notes = rv_get.get_json()
    assert notes[0]["title"] == "Updated Title"
    assert notes[0]["body"] == "Updated body"

def test_update_nonexistent_note(client):
    rv = client.put('/api/notes/999', json={"title": "Nope"})
    assert rv.status_code == 404

def test_delete_note(client):
    rv_create = client.post('/api/notes', json={
        "title": "Delete Me",
        "body": "Delete body"
    })
    note_id = rv_create.get_json()["id"]
    
    rv_delete = client.delete(f'/api/notes/{note_id}')
    assert rv_delete.status_code == 200
    assert rv_delete.get_json() == {"message": "Note deleted"}
    
    rv_get = client.get('/api/notes')
    assert len(rv_get.get_json()) == 0

def test_delete_nonexistent_note(client):
    rv = client.delete('/api/notes/999')
    assert rv.status_code == 404
