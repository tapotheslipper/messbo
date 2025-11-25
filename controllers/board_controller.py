from database import get_connection
from models import Logger, Board
from datetime import datetime, timezone
import sqlite3

logger = Logger().get_logger()


class BoardController:
    def __init__(self):
        pass

    def count_user_boards(self, user_id: int) -> int:
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            cur.execute("SELECT COUNT(*) FROM boards WHERE owner_id = ?", (user_id,))
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
            if board_name:
                board_name = " ".join(board_name.strip().split())

            if not board_name or board_name.startswith("/"):
                count = self.count_user_boards(user_id) + 1
                board_name = f"board{count}"

            board = Board(
                owner_id = user_id,
                name = board_name,
            )

            cur.execute(
                "INSERT INTO boards (name, owner_id, created_at_utc, last_modified_at_utc) VALUES (?, ?, ?, ?)",
                (
                    board.name,
                    board.owner_id,
                    board.created_at_utc.isoformat(),
                    board.last_modified_at_utc.isoformat(),
                ),
            )

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
            boards_list = [row['name'] for row in cur.fetchall()]
            return boards_list
        except Exception as exc:
            logger.error(f"Error showing all boards: '{exc}'")
            return []
        finally:
            con.close()

    def show_one_board(self, owner_id: int, board_name: str):
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            cur.execute(
                "SELECT * FROM boards WHERE owner_id = ? AND name = ?",
                (owner_id, board_name),
            )
            row = cur.fetchone()

            if row is None:
                return None

            board = self._row_to_board(row)
            return board
        except Exception as exc:
            logger.error(f"Error showing one board: '{exc}'")
            return None
        finally:
            con.close()

    def rename_board(self, owner_id: int, old_name: str, new_name: str):
        con = self._create_con()
        cur = self._create_cur(con)
        try:
            logger.info(f"Attempting to rename '{old_name}' to '{new_name}' for user {owner_id}.")
            cur.execute(
                "SELECT * FROM boards WHERE owner_id = ? AND name = ?",
                (owner_id, old_name)
            )
            row = cur.fetchone()
            if row:
                board = self._row_to_board(row)
                board.set_name(new_name)
            
                cur.execute(
                    "UPDATE boards SET name = ?, last_modified_at_utc = ? WHERE owner_id = ? AND name = ?",
                    (
                        board.name,
                        board.last_modified_at_utc.isoformat(),
                        owner_id,
                        old_name
                    ),
                )
                con.commit()
                logger.info(f"Board '{old_name}' renamed to '{new_name}' by user '{owner_id}'.")
                return True
            else:
                return False
        except Exception as exc:
            logger.error(f"Error renaming board from '{old_name}' to '{new_name}' by user '{owner_id}': '{exc}'")
            con.rollback()
            return None
        finally:
            con.close()

    def _row_to_board(self, row):
        return Board(
            id = row['id'],
            name = row['name'],
            owner_id = row['owner_id'],
            created_at_utc = datetime.fromisoformat(row['created_at_utc']),
            last_modified_at_utc = datetime.fromisoformat(row['last_modified_at_utc'])
        )

    def _create_con(self):
        return get_connection()

    def _create_cur(self, connection):
        return connection.cursor()
