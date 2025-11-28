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
            chat_id INTEGER NOT NULL,
            owner_id INTEGER NOT NULL,
            created_at_utc TEXT NOT NULL,
            last_modified_at_utc TEXT NOT NULL,
            UNIQUE(name, chat_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS board_access (
            board_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(board_id, user_id),
            FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            board_id INTEGER NOT NULL,
            requester_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(status IN ('pending', 'accepted', 'denied')),
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_owner_name
        ON boards (owner_id, name)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_board_access
        ON board_access (board_id, user_id)
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS idx_access_requests
        ON access_requests (chat_id, board_id, status)
        """
    )

    con.commit()
    con.close()
