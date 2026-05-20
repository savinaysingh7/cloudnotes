const API_URL = '/api/notes';
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
    loadNotes();
    document.getElementById('add-note').addEventListener('click', addNote);
    document.getElementById('search-input').addEventListener('input', handleSearch);
    // Allow Enter key to submit note
    document.getElementById('note-body').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') addNote();
    });
});

function handleSearch(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        loadNotes(e.target.value.trim());
    }, 300);
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function formatTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

async function loadNotes(search = '') {
    showLoading(true);
    try {
        const url = search ? `${API_URL}?search=${encodeURIComponent(search)}` : API_URL;
        const response = await fetch(url);
        const notes = await response.json();
        const notesList = document.getElementById('notes-list');
        const notesCount = document.getElementById('notes-count');

        notesCount.textContent = `${notes.length} note${notes.length !== 1 ? 's' : ''}`;
        notesList.innerHTML = '';

        if (notes.length === 0) {
            notesList.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <p>${search ? 'No notes match your search.' : 'No notes yet. Create your first note above!'}</p>
                </div>
            `;
            showLoading(false);
            return;
        }

        notes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.className = 'note-item';
            noteElement.innerHTML = `
                <h3>${escapeHtml(note.title)}</h3>
                <p>${escapeHtml(note.body)}</p>
                <div class="note-meta">
                    <span class="note-time">${formatTime(note.created_at)}</span>
                    <div class="note-actions">
                        <button class="btn btn-edit" onclick="openEditModal(${note.id}, '${escapeAttr(note.title)}', '${escapeAttr(note.body)}')">Edit</button>
                        <button class="btn btn-delete" onclick="deleteNote(${note.id})">Delete</button>
                    </div>
                </div>
            `;
            notesList.appendChild(noteElement);
        });
    } catch (error) {
        console.error('Error loading notes:', error);
        showToast('Failed to load notes', 'error');
    }
    showLoading(false);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeAttr(text) {
    return text.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
}

async function addNote() {
    const titleEl = document.getElementById('note-title');
    const bodyEl = document.getElementById('note-body');
    const title = titleEl.value.trim();
    const body = bodyEl.value.trim();

    if (!title || !body) {
        showToast('Please fill in both title and body', 'error');
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, body })
        });

        if (response.ok) {
            titleEl.value = '';
            bodyEl.value = '';
            showToast('Note created successfully!');
            loadNotes();
        } else {
            const err = await response.json();
            showToast(err.error || 'Failed to create note', 'error');
        }
    } catch (error) {
        console.error('Error adding note:', error);
        showToast('Network error — could not create note', 'error');
    }
}

function openEditModal(id, title, body) {
    document.getElementById('edit-note-id').value = id;
    document.getElementById('edit-note-title').value = title;
    document.getElementById('edit-note-body').value = body;
    document.getElementById('edit-modal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

async function saveEdit() {
    const id = document.getElementById('edit-note-id').value;
    const title = document.getElementById('edit-note-title').value.trim();
    const body = document.getElementById('edit-note-body').value.trim();

    if (!title || !body) {
        showToast('Please fill in both fields', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, body })
        });

        if (response.ok) {
            closeEditModal();
            showToast('Note updated!');
            loadNotes();
        } else {
            showToast('Failed to update note', 'error');
        }
    } catch (error) {
        console.error('Error updating note:', error);
        showToast('Network error — could not update', 'error');
    }
}

async function deleteNote(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showToast('Note deleted');
            loadNotes();
        } else {
            showToast('Failed to delete note', 'error');
        }
    } catch (error) {
        console.error('Error deleting note:', error);
        showToast('Network error — could not delete', 'error');
    }
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeEditModal();
});

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'edit-modal') closeEditModal();
});
