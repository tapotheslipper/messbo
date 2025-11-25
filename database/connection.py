from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "bot.db"


def get_connection(db_file=DB_PATH):
    con = sqlite3.connect(db_file, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def initialize_db():
    con = get_connection()
    cursor = con.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            owner_id INTEGER NOT NULL,
            created_at_utc TEXT NOT NULL,
            last_modified_at_utc TEXT NOT NULL
        )"""
    )
    con.commit()
    con.close()
