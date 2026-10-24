import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_FILE = 'alif_lab.db'

def init_db():
    # Remove existing db if exists for clean slate
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        points INTEGER DEFAULT 0,
        full_name TEXT DEFAULT '',
        school TEXT DEFAULT '',
        address TEXT DEFAULT '',
        bio TEXT DEFAULT '',
        profile_picture TEXT DEFAULT 'default_avatar.png'
    )
    ''')

    # Create Blogs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'Blue Team',
        author_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users (id)
    )
    ''')

    # Create Chat Messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER, -- NULL for public chat
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (receiver_id) REFERENCES users (id)
    )
    ''')

    # Create Chat Requests table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending', -- pending, accepted, declined
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (receiver_id) REFERENCES users (id)
    )
    ''')

    # Pre-populate Admin
    admin_password = generate_password_hash('admin123')
    cursor.execute('INSERT INTO users (unique_id, username, password, role, points) VALUES (?, ?, ?, ?, ?)', 
                   ('ADMIN-000', 'admin', admin_password, 'admin', 0))

    # Pre-populate Participants
    participants = [
        ('BD-001', 'Budi Santoso', 'password123', 150),
        ('SA-002', 'Siti Aminah', 'password123', 200),
        ('AW-003', 'Agus Wijaya', 'password123', 50)
    ]

    for p in participants:
        hashed_pw = generate_password_hash(p[2])
        cursor.execute('INSERT INTO users (unique_id, username, password, role, points) VALUES (?, ?, ?, ?, ?)', 
                       (p[0], p[1], hashed_pw, 'participant', p[3]))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
