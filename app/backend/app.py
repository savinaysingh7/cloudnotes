from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///notes.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
metrics = PrometheusMetrics(app)

# Custom metrics
notes_created = metrics.counter(
    'notes_created_total',
    'Total number of notes created'
)
notes_deleted = metrics.counter(
    'notes_deleted_total',
    'Total number of notes deleted'
)

class Note(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body  = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    return jsonify([{"id": n.id, "title": n.title, "body": n.body}
                    for n in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or 'title' not in data or 'body' not in data:
        return jsonify({"error": "Missing title or body"}), 400
    note = Note(title=data['title'], body=data['body'])
    db.session.add(note)
    db.session.commit()
    notes_created.inc()
    return jsonify({"id": note.id, "message": "Note created"}), 201

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    notes_deleted.inc()
    return jsonify({"message": "Note deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
