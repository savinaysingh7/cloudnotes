from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timezone
import os

app = Flask(__name__)
database_url = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
# SQLAlchemy 2.1 defaults bare PostgreSQL URLs to psycopg 3. This project
# installs psycopg2-binary, so select that driver explicitly for compatibility.
if database_url.startswith('postgresql://'):
    database_url = database_url.replace(
        'postgresql://', 'postgresql+psycopg2://', 1
    )
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
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
notes_active_gauge = Gauge(
    'cloudnotes_notes_total',
    'Current number of notes in database'
)

class Note(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(100), nullable=False)
    body       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

_db_initialized = False

def init_db():
    global _db_initialized
    if _db_initialized:
        return True
    try:
        db.create_all()
        from sqlalchemy import text, inspect
        inspector = inspect(db.engine)
        if 'note' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('note')]
            if 'created_at' not in columns:
                db.session.execute(text(
                    'ALTER TABLE note ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                ))
                db.session.commit()
        _db_initialized = True
        return True
    except Exception as e:
        app.logger.warning(f"Database initialization deferred: {e}")
        return False

with app.app_context():
    init_db()

@app.before_request
def ensure_database_ready():
    global _db_initialized
    if not _db_initialized and request.endpoint not in ('health', 'metrics_endpoint'):
        init_db()

@app.route('/metrics')
def metrics_endpoint():
    try:
        notes_active_gauge.set(Note.query.count())
    except Exception:
        pass
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/api/health')
def health():
    db_check = request.args.get('db', '0')
    if db_check == '1':
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            init_db()
            return jsonify({"status": "ok", "database": "connected"})
        except Exception as e:
            return jsonify({"status": "degraded", "database": str(e)}), 503
    return jsonify({"status": "ok"})

def serialize_created_at(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).isoformat()
    return dt.isoformat()

@app.route('/api/notes', methods=['GET'])
def get_notes():
    search = request.args.get('search', '').strip()
    if search:
        notes = Note.query.filter(
            Note.title.ilike(f'%{search}%') | Note.body.ilike(f'%{search}%')
        ).order_by(Note.created_at.desc(), Note.id.desc()).all()
    else:
        notes = Note.query.order_by(Note.created_at.desc(), Note.id.desc()).all()
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "body": n.body,
        "created_at": serialize_created_at(n.created_at)
    } for n in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
    if 'title' not in data or 'body' not in data:
        return jsonify({"error": "Missing title or body"}), 400
    if data['title'] is None or data['body'] is None:
        return jsonify({"error": "Title and body cannot be null"}), 400
    if not isinstance(data['title'], str) or not isinstance(data['body'], str):
        return jsonify({"error": "Title and body must be strings"}), 400
    title = data['title'].strip()
    body = data['body'].strip()
    if not title or not body:
        return jsonify({"error": "Title and body cannot be empty"}), 400
    if len(title) > 100:
        return jsonify({"error": "Title must not exceed 100 characters"}), 400
    note = Note(title=title, body=body)
    try:
        db.session.add(note)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to create note: {e}")
        return jsonify({"error": "Database error"}), 500
    notes_created_counter.inc()
    return jsonify({"id": note.id, "message": "Note created"}), 201

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    note = db.get_or_404(Note, note_id)
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "No data provided"}), 400
    if 'title' in data:
        if data['title'] is None or not isinstance(data['title'], str):
            return jsonify({"error": "Title must be a non-null string"}), 400
        new_title = data['title'].strip()
        if not new_title:
            return jsonify({"error": "Title cannot be empty"}), 400
        if len(new_title) > 100:
            return jsonify({"error": "Title must not exceed 100 characters"}), 400
        note.title = new_title
    if 'body' in data:
        if data['body'] is None or not isinstance(data['body'], str):
            return jsonify({"error": "Body must be a non-null string"}), 400
        new_body = data['body'].strip()
        if not new_body:
            return jsonify({"error": "Body cannot be empty"}), 400
        note.body = new_body
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to update note: {e}")
        return jsonify({"error": "Database error"}), 500
    notes_updated_counter.inc()
    return jsonify({"id": note.id, "message": "Note updated"})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = db.get_or_404(Note, note_id)
    try:
        db.session.delete(note)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to delete note: {e}")
        return jsonify({"error": "Database error"}), 500
    notes_deleted_counter.inc()
    return jsonify({"message": "Note deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
