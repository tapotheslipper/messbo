import sqlite3

def get_connection(db_file = "database/bot.db"):
    con = sqlite3.connect(db_file, check_same_thread=False)
    return con

def initialize_db():
    con = get_connection()
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL
        )
    """)
    con.commit()
    con.close()
