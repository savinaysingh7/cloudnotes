from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///notes.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for all routes
metrics = PrometheusMetrics(app, path=None) # Disable automatic path

# Custom metrics
notes_created_counter = Counter(
    'notes_created_total',
    'Total number of notes created'
)
notes_deleted_counter = Counter(
    'notes_deleted_total',
    'Total number of notes deleted'
)
notes_updated_counter = Counter(
    'notes_updated_total',
    'Total number of notes updated'
)

class Note(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(100), nullable=False)
    body       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

with app.app_context():
    db.create_all()
    # Auto-migrate: add created_at column if it doesn't exist on an older DB
    try:
        from sqlalchemy import text, inspect
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('note')]
        if 'created_at' not in columns:
            db.session.execute(text(
                'ALTER TABLE note ADD COLUMN created_at TIMESTAMP DEFAULT NOW()'
            ))
            db.session.commit()
    except Exception:
        pass  # Table may not exist yet (first run) — db.create_all() handles it

@app.route('/metrics')
def metrics_endpoint():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/notes', methods=['GET'])
def get_notes():
    search = request.args.get('search', '').strip()
    if search:
        notes = Note.query.filter(
            Note.title.ilike(f'%{search}%') | Note.body.ilike(f'%{search}%')
        ).all()
    else:
        notes = Note.query.all()
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "body": n.body,
        "created_at": n.created_at.isoformat() + 'Z' if n.created_at else None
    } for n in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or 'title' not in data or 'body' not in data:
        return jsonify({"error": "Missing title or body"}), 400
    note = Note(title=data['title'], body=data['body'])
    db.session.add(note)
    db.session.commit()
    notes_created_counter.inc()
    return jsonify({"id": note.id, "message": "Note created"}), 201

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    note.title = data.get('title', note.title)
    note.body = data.get('body', note.body)
    db.session.commit()
    notes_updated_counter.inc()
    return jsonify({"id": note.id, "message": "Note updated"})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    notes_deleted_counter.inc()
    return jsonify({"message": "Note deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
