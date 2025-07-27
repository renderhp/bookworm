import sqlite3
import json

DATABASE_NAME = "bookworm.db"

def connect_db():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        # Config table for API key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                file_path TEXT UNIQUE NOT NULL
            )
        """)
        # Chapters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                embedding BLOB,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """)
        conn.commit()

def insert_book(title, author, file_path):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, file_path) VALUES (?, ?, ?)", (title, author, file_path))
        conn.commit()
        return cursor.lastrowid

def insert_chapter(book_id, chapter_number, content, embedding=None, summary=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        # Convert embedding list to JSON string and then to bytes
        embedding_data = json.dumps(embedding).encode('utf-8') if embedding is not None else None
        cursor.execute("INSERT INTO chapters (book_id, chapter_number, content, embedding, summary) VALUES (?, ?, ?, ?, ?)", (book_id, chapter_number, content, embedding_data, summary))
        conn.commit()

def set_api_key(api_key):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", ("gemini_api_key", api_key))
        conn.commit()

def get_api_key():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", ("gemini_api_key",))
        result = cursor.fetchone()
        return result[0] if result else None

def get_chapters_for_book(book_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chapter_number, content, embedding, summary FROM chapters WHERE book_id = ? ORDER BY chapter_number", (book_id,))
        rows = cursor.fetchall()
        # Decode embedding from BLOB to list
        return [(row[0], row[1], json.loads(row[2].decode('utf-8')) if row[2] else None, row[3]) for row in rows]

def get_book_by_title(title):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, file_path FROM books WHERE title = ?", (title,))
        return cursor.fetchone()

def purge_data():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chapters")
        cursor.execute("DELETE FROM books")
        conn.commit()
        print("All book and chapter data purged from the database.")

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
