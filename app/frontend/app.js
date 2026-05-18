const API_URL = '/api/notes';

document.addEventListener('DOMContentLoaded', () => {
    loadNotes();

    document.getElementById('add-note').addEventListener('click', addNote);
});

async function loadNotes() {
    try {
        const response = await fetch(API_URL);
        const notes = await response.json();
        const notesList = document.getElementById('notes-list');
        notesList.innerHTML = '';
        notes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.className = 'note-item';
            noteElement.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.body}</p>
                <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
            `;
            notesList.appendChild(noteElement);
        });
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

async function addNote() {
    const title = document.getElementById('note-title').value;
    const body = document.getElementById('note-body').value;

    if (!title || !body) return alert('Please fill in both fields');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, body })
        });

        if (response.ok) {
            document.getElementById('note-title').value = '';
            document.getElementById('note-body').value = '';
            loadNotes();
        }
    } catch (error) {
        console.error('Error adding note:', error);
    }
}

async function deleteNote(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadNotes();
        }
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}
