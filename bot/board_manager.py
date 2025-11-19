from database import get_connection
from models import Logger
from models import Board

logger = Logger().get_logger()

class BoardManager:
    def __init__(self):
        self.con = get_connection()
        self.cursor = self.con.cursor()

    def count_user_boards(self, user_id) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM boards WHERE owner_id = ?", (user_id))
        return self.cursor.fetchone()[0]

    def create_board(self, user_id: int, board_name: str | None):
        try:
            if (board_name):
                board_name = " ".join(board_name.strip().split())
            
            if (not board_name or board_name.startsWith("/")):
                count = self.count_user_boards(user_id) + 1
                board_name = f"board{count}"

            board = Board(owner_id = user_id, board_name = board_name)
            
            self.cursor.execute("
                INSERT INTO boards (name, owner_id) VALUES (?, ?)",
                (board.board_name, board.owner_id)
            )
            self.con.commit()
            logger.info(f"Board '{board.board_name}' created by user '{board.owner_id}'")
            return board
        except Exception as exc:
            logger.error(f"Error creating board: '{exc}'")
            self.con.rollback()
