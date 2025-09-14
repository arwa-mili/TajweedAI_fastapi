import sqlite3
import os
from .config import settings

def init_db():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            chunk_sequence INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration_ms INTEGER,
            file_size INTEGER,
            actual_duration_ms REAL,
            sura_number INTEGER,
            ayat_begin INTEGER,
            ayat_end INTEGER,
            word_begin INTEGER,
            word_end INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(settings.DB_PATH)
