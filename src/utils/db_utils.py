from pathlib import Path
import sqlite3
from prompt_toolkit import prompt
from rich import print

from constants import (
    DB_APP_SETTINGS_TABLE,
    DB_BOOKS_TABLE,
    DB_PATH,
    DB_SNIPPETS_TABLE,
)


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
            f"""
                CREATE TABLE IF NOT EXISTS {DB_BOOKS_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
        )

        cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {DB_SNIPPETS_TABLE} (
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
            f"""
                CREATE TABLE IF NOT EXISTS {DB_APP_SETTINGS_TABLE} (
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
    c.execute(
        f"INSERT OR REPLACE INTO {DB_APP_SETTINGS_TABLE} VALUES (?, ?)", (key, value)
    )
    conn.commit()
    conn.close()
