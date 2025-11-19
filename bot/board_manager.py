from database import get_connection
from models import Logger
from models import Board

logger = Logger().get_logger()

class BoardManager:
    def __init__(self):
        pass

    def count_user_boards(self, user_id) -> int:
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            cur.execute(
                "SELECT COUNT(*) FROM boards WHERE owner_id = ?",
                (user_id,)
            )
            return cur.fetchone()[0]
        except Exception as exc:
            logger.error(f"Error counting user's boards: {exc}")
            return 0
        finally:
            con.close()

    def create_board(self, user_id: int, board_name: str | None):
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            if (board_name):
                board_name = " ".join(board_name.strip().split())
            
            if (not board_name or board_name.startswith("/")):
                count = self.count_user_boards(user_id) + 1
                board_name = f"board{count}"
            
            board = Board(owner_id = user_id, board_name = board_name)

            cur.execute(
                "INSERT INTO boards (name, owner_id) VALUES (?, ?)",
                (board.name, board.owner_id)
            )

            board.id = cur.lastrowid
            
            con.commit()
            logger.info(f"Board '{board.name}' created by user '{board.owner_id}'")
            return board
        except Exception as exc:
            logger.error(f"Error creating board: '{exc}'")
            con.rollback()
            return None
        finally:
            con.close()

    def show_all_boards(self, owner_id: int):
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            cur.execute(
                "SELECT name FROM boards WHERE owner_id = ?",
                (owner_id,)
            )
            boards_list = [row[0] for row in cur.fetchall()]
            return boards_list
        except Exception as exc:
            logger.error(f"Error showing all boards: '{exc}'")
            con.rollback()
            return []
        finally:
            con.close()
    
    def show_one_board(self, owner_id: int, board_name: str):
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            cur.execute(
                "SELECT name FROM boards WHERE owner_id = ? AND name = ?",
                (owner_id, board_name)
            )
            row = cur.fetchone()
            return row[0] if row else None
        except Exception as exc:
            logger.error(f"Error showing one board: '{exc}'")
            con.rollback()
            return None
        finally:
            con.close()

    def _create_con(self):
        return get_connection()

    def _create_cur(self, connection):
        return connection.cursor()
