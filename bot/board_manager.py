from database import get_connection
from models import Logger

logger = Logger().get_logger()

class BoardManager:
    def __init__(self):
        self.con = get_connection()
        self.cursor = self.con.cursor()

    def create_board(self, user_id: int):
        try:
            self.cursor.execute("INSERT INTO boards (owner_id) VALUES (?)", (user_id,))
            self.con.commit()
        except Exception as exc:
            logger.error(f"Error creating board: {exc}")
            self.con.rollback()
