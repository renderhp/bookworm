from pathlib import Path
import sqlite3
from prompt_toolkit import prompt
from rich import print

from constants import DB_PATH


def create_db(*args):
    db_path = Path(DB_PATH)

    if db_path.exists() and "--force" not in args:
        print("[yellow]Database already exists. Use --force to recreate.[/yellow]")
        return

    if "--force" in args:
        yn = prompt("This will completely wipe the DB. Are you sure? (y/n): ")
        if yn != "y":
            return

        db_path.unlink()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
        )

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER,
                    snippet TEXT,
                    summary TEXT,
                    embedding TEXT,
                    FOREIGN KEY (book_id) REFERENCES books(id)
                )
            """
        )

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY, 
                    value TEXT
                )
            """
        )

        # Commit changes and close connection
        conn.commit()
        conn.close()

        print("[green]Database initialized successfully![/green]")

    except sqlite3.Error as e:
        print(f"[red]Error creating database: {e}[/red]")

    except Exception as e:
        print(f"[red]Unexpected error: {e}[/red]")


def set_setting(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO app_settings VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
