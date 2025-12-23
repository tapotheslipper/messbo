from database import get_connection
from models import Logger, Board, BoardEntry
from datetime import datetime, timezone
import sqlite3
import traceback

logger = Logger().get_logger()


class BoardController:
    def __init__(self):
        pass

    def _create_con(self):
        con = get_connection()
        cur = con.cursor()
        return con, cur

    def create_board(
        self, chat_id: int, user_id: int, board_name: str | None
    ) -> tuple[Board | None, str]:
        con, cur = self._create_con()
        try:
            if board_name:
                board_name = board_name.strip().strip("'\"` ")
                board_name = " ".join(board_name.split())

            if not board_name or board_name.startswith("/"):
                next_num = self._get_max_board_number(chat_id) + 1
                board_name = f"board{next_num}"

            board = Board(
                name=board_name,
                chat_id=chat_id,
                owner_id=user_id,
            )

            with con:
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
            return None, board_name or "автосгенерированная доска"
        finally:
            con.close()

    def show_all_boards(self, chat_id: int) -> list:
        con, cur = self._create_con()
        try:
            cur.execute("SELECT name FROM boards WHERE chat_id = ?", (chat_id,))
            return [row["name"] for row in cur.fetchall()]
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

            return self._row_to_board(row) if row else None
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
            board = self.show_one_board(chat_id, old_name)
            if not board:
                return "not_found"

            if not self._has_access(board.id, user_id):
                return "no_access"

            if self.show_one_board(chat_id, new_name):
                return "name_taken"

            board.set_name(new_name)
            with con:
                cur.execute(
                    "UPDATE boards SET name = ?, last_modified_at_utc = ? WHERE id = ?",
                    (board.name, board.last_modified_at_utc.isoformat(), board.id),
                )
            return "renamed"
        except Exception as exc:
            logger.error(
                f"Error renaming board from '{old_name}' to '{new_name}' in chat '{chat_id}' by user '{user_id}': '{exc}'."
            )
            return "error"
        finally:
            con.close()

    def remove_board(self, chat_id: int, user_id: int, board_name: str) -> bool:
        con, cur = self._create_con()
        try:
            with con:
                cur.execute(
                    "DELETE FROM boards WHERE chat_id = ? AND name = ? AND owner_id = ?",
                    (chat_id, board_name, user_id),
                )
                return cur.rowcount > 0
        except Exception as exc:
            logger.error(
                f"Error removing board '{board_name}' in chat '{chat_id}' by user '{user_id}': '{exc}'."
            )
            return False
        finally:
            con.close()

    # board entries

    def add_entry(self, board_id: int, user_id: int, content: str) -> bool:
        con, cur = self._create_con()
        try:
            with con:
                cur.execute(
                    "SELECT MAX(local_id) FROM entries WHERE board_id = ?", (board_id,)
                )
                res = cur.fetchone()[0]
                next_local_id = (res + 1) if res is not None else 1

                entry = BoardEntry(
                    board_id=board_id,
                    user_id=user_id,
                    content=content,
                    local_id=next_local_id,
                )

                cur.execute(
                    "INSERT INTO entries (board_id, local_id, user_id, content, created_at_utc, last_modified_at_utc) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        entry.board_id,
                        entry.local_id,
                        entry.user_id,
                        entry.content,
                        entry.created_at_utc.isoformat(),
                        entry.last_modified_at_utc.isoformat(),
                    ),
                )
            return True
        except Exception as exc:
            error_details = traceback.format_exc()
            logger.error(f"[ADD ENTRY ERROR]: '{error_details}'")
            return False
        finally:
            con.close()

    def edit_entry(self, entry_id: int, new_content: str) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cur.fetchone()
            if not row:
                return False

            entry = self._row_to_entry(row)
            entry.set_content(new_content)

            with con:
                cur.execute(
                    "UPDATE entries SET content = ?, last_modified_at_utc = ? WHERE id = ?",
                    (entry.content, entry.last_modified_at_utc.isoformat(), entry.id),
                )
                return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error editing entry: '{exc}'")
            return False
        finally:
            con.close()

    def delete_entry(self, entry_id: int) -> bool:
        con, cur = self._create_con()
        try:
            with con:
                cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error removing entry: '{exc}'")
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

    def _get_max_board_number(self, chat_id: int) -> int:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT MAX(CAST(SUBSTR(name, 6) AS INTEGER)) FROM boards WHERE chat_id = ? AND name LIKE 'board%'",
                (chat_id,),
            )
            res = cur.fetchone()[0]
            return res if res is not None else 0
        except Exception as exc:
            logger.error(f"Error finding max board number in caht '{chat_id}': '{exc}'")
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
            return cur.fetchone() is not None
        finally:
            con.close()

    def _row_to_board(self, row) -> Board:
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

    def get_board_moderators(self, board_id: int) -> list[int]:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT ba.user_id FROM board_access ba JOIN boards b on ba.board_id = b.id WHERE ba.board_id = ? AND ba.user_id != b.owner_id",
                (board_id,),
            )
            return [row["user_id"] for row in cur.fetchall()]
        except Exception as exc:
            logger.error(f"Error fetching moderators: '{exc}'")
            return []
        finally:
            con.close()

    def get_board_entries(self, board_id: int) -> list:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT * FROM entries WHERE board_id = ? ORDER BY last_modified_at_utc DESC",
                (board_id,),
            )
            return cur.fetchall()
        except Exception as exc:
            logger.error(f"Error getting board entries: '{exc}'")
            return []
        finally:
            con.close()

    def get_entry_by_local_id(self, board_id: int, local_id: int) -> BoardEntry | None:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT * FROM entries WHERE board_id = ? AND local_id = ?",
                (
                    board_id,
                    entry_id,
                ),
            )
            row = cur.fetchone()
            return self._row_to_entry(row) if row else None
        finally:
            con.close()

    def _row_to_entry(self, row) -> BoardEntry:
        return BoardEntry(
            id=row["id"],
            board_id=row["board_id"],
            local_id=row["local_id"],
            user_id=row["user_id"],
            content=row["content"],
            created_at_utc=datetime.fromisoformat(row["created_at_utc"]),
            last_modified_at_utc=datetime.fromisoformat(row["last_modified_at_utc"]),
        )
