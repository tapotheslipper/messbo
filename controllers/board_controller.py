from database import get_connection
from models import Logger, Board
from datetime import datetime, timezone
import sqlite3

logger = Logger().get_logger()


class BoardController:
    def __init__(self):
        pass

    def create_board(
        self, chat_id: int, user_id: int, board_name: str | None
    ) -> tuple[Board | None, str]:
        con, cur = self._create_con()
        try:
            if board_name:
                board_name = " ".join(board_name.strip().split())

            if not board_name or board_name.startswith("/"):
                cur.execute(
                    "SELECT COUNT(*) FROM boards WHERE chat_id = ?",
                    (chat_id,),
                )
                count = cur.fetchone()[0] + 1
                board_name = f"board{count}"

            board = Board(
                name=board_name,
                chat_id=chat_id,
                owner_id=user_id,
            )

            cur.execute(
                "INSERT INTO boards (name, chat_id, owner_id, created_at_utc, last_modified_at_utc) VALUES (?, ?, ?, ?, ?)",
                (
                    board.name,
                    board.chat_id,
                    board.owner_id,
                    board.created_at_utc.isoformat(),
                    board.last_modified_at_utc.isoformat(),
                ),
            )
            board.id = cur.lastrowid

            cur.execute(
                "INSERT INTO board_access (board_id, user_id) VALUES (?, ?)",
                (board.id, board.owner_id),
            )

            con.commit()
            logger.info(
                f"Board '{board.name}' created in chat '{board.chat_id}' by user '{board.owner_id}'."
            )
            return board, board.name
        except sqlite3.IntegrityError:
            logger.warning(
                f"Duplicate board name attempt: '{board_name}' by user '{user_id}'."
            )
            return None, board_name
        except Exception as exc:
            logger.error(f"Error creating board: '{exc}'.")
            con.rollback()
            return None, board_name if board_name else "автосгенерированная доска"
        finally:
            con.close()

    def show_all_boards(self, chat_id: int) -> list:
        con, cur = self._create_con()
        try:
            cur.execute("SELECT name FROM boards WHERE chat_id = ?", (chat_id,))
            boards_list = [row["name"] for row in cur.fetchall()]
            return boards_list
        except Exception as exc:
            logger.error(f"Error showing all boards: '{exc}'.")
            return []
        finally:
            con.close()

    def show_one_board(self, chat_id: int, board_name: str) -> Board | None:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT * FROM boards WHERE chat_id = ? AND name = ?",
                (chat_id, board_name),
            )
            row = cur.fetchone()

            if row is None:
                return None

            board = self._row_to_board(row)
            return board
        except Exception as exc:
            logger.error(f"Error showing one board: '{exc}'.")
            return None
        finally:
            con.close()

    def rename_board(
        self, chat_id: int, user_id: int, old_name: str, new_name: str
    ) -> str:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT * FROM boards WHERE chat_id = ? AND name = ?",
                (chat_id, old_name),
            )
            row = cur.fetchone()

            if not row:
                logger.warning(
                    f"Board '{old_name}' in chat '{chat_id}' not found for renaming."
                )
                return "not_found"

            board = self._row_to_board(row)

            if not self._has_access(board.id, user_id):
                logger.warning(
                    f"User '{user_id}' has no access to rename board '{old_name}'."
                )
                return "no_access"

            cur.execute(
                "SELECT 1 FROM boards WHERE chat_id = ? AND name = ?",
                (
                    chat_id,
                    new_name,
                ),
            )
            if cur.fetchone():
                logger.warning(
                    f"Board name '{new_name}' already exists in chat '{chat_id}'."
                )
                return "name_taken"

            board.set_name(new_name)
            cur.execute(
                "UPDATE boards SET name = ?, last_modified_at_utc = ? WHERE id = ?",
                (
                    board.name,
                    board.last_modified_at_utc.isoformat(),
                    board.id,
                ),
            )

            con.commit()
            logger.info(
                f"Board '{old_name}' renamed to '{new_name}' by user '{user_id}' in chat '{chat_id}'."
            )
            return "renamed"
        except sqlite3.IntegrityError:
            logger.warning(
                f"Duplicate board name '{old_name}' attempt renaming to '{new_name}' by user '{user_id}' in chat '{chat_id}'."
            )
            return "name_taken"
        except Exception as exc:
            logger.error(
                f"Error renaming board from '{old_name}' to '{new_name}' by user '{user_id}': '{exc}'."
            )
            con.rollback()
            return None
        finally:
            con.close()

    def remove_board(self, chat_id: int, user_id: int, board_name: str) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT id FROM boards WHERE chat_id = ? AND name = ? AND owner_id = ?",
                (
                    chat_id,
                    board_name,
                    user_id,
                ),
            )
            row = cur.fetchone()
            if not row:
                return False

            cur.execute(
                "DELETE FROM boards WHERE id = ?",
                (row["id"],),
            )

            con.commit()
            logger.info(
                f"Board '{board_name}' is removed by user '{user_id}' in chat '{chat_id}'."
            )
            return True
        except Exception as exc:
            logger.error(
                f"Error removing board '{board_name}' by user '{user_id}': {exc}."
            )
            con.rollback()
            return False
        finally:
            con.close()

    def remove_access(
        self, chat_id: int, board_id: int, owner_id: int, remove_user_id: int
    ) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT 1 FROM boards WHERE chat_id = ? AND owner_id = ? AND id = ?",
                (
                    chat_id,
                    owner_id,
                    board_id,
                ),
            )
            if not cur.fetchone():
                return False

            cur.execute(
                "SELECT 1 FROM board_access WHERE board_id = ? AND user_id = ?",
                (
                    board_id,
                    remove_user_id,
                ),
            )
            if not cur.fetchone():
                return False

            cur.execute(
                "DELETE FROM board_access WHERE board_id = ? AND user_id = ?",
                (
                    board_id,
                    remove_user_id,
                ),
            )

            con.commit()
            logger.info(
                f"Board '{board_id}' editing access is taken from user '{remove_user_id}' by user '{owner_id}'."
            )
        except Exception as exc:
            logger.error(f"Error removing access: '{exc}'.")
            return False
        finally:
            con.close()

    # supplementary methods

    def _count_chat_boards(self, chat_id: int) -> int:
        con, cur = self._create_con()
        try:
            cur.execute("SELECT COUNT(*) FROM boards WHERE chat_id = ?", (chat_id,))
            return cur.fetchone()[0]
        except Exception as exc:
            logger.error(f"Error counting chat '{chat_id}' boards: {exc}.")
            return 0
        finally:
            con.close()

    def _has_access(self, board_id: int, user_id: int) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT 1 FROM board_access WHERE board_id = ? AND user_id = ?",
                (board_id, user_id),
            )
            access = cur.fetchone()
            return access is not None
        finally:
            con.close()

    def _row_to_board(self, row):
        return Board(
            id=row["id"],
            name=row["name"],
            chat_id=row["chat_id"],
            owner_id=row["owner_id"],
            created_at_utc=datetime.fromisoformat(row["created_at_utc"]),
            last_modified_at_utc=datetime.fromisoformat(row["last_modified_at_utc"]),
        )

    def get_name_by_id(self, board_id: int) -> str | None:
        con, cur = self._create_con()
        try:
            cur.execute("SELECT name FROM boards WHERE id = ?", (board_id,))
            row = cur.fetchone()
            return row["name"] if row else None
        except Exception as exc:
            logger.error(f"Error fetching board name by id: {exc}")
            return None
        finally:
            con.close()

    def _create_con(self):
        con = get_connection()
        cur = con.cursor()
        return con, cur
