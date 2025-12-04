from database import get_connection
from models import Logger, Request
from datetime import datetime, timezone
import sqlite3
import uuid

logger = Logger().get_logger()


class RequestController:
    def __init__(self):
        pass

    def add_mod_request(
        self,
        chat_id: int,
        board_id: int,
        requester_id: int,
        target_id: int,
        message_id: int,
    ) -> str | None:
        con, cur = self._create_con()
        try:
            token = str(uuid.uuid4())

            request = Request(
                token=token,
                chat_id=chat_id,
                board_id=board_id,
                requester_id=requester_id,
                target_id=target_id,
                message_id=message_id,
                type="mod",
            )

            cur.execute(
                "INSERT INTO requests (token, chat_id, board_id, requester_id, target_id, message_id, type, created_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    request.token,
                    request.chat_id,
                    request.board_id,
                    request.requester_id,
                    request.target_id,
                    request.message_id,
                    request.type,
                    request.created_at_utc.isoformat(),
                ),
            )
            con.commit()
            return token
        except Exception as exc:
            logger.error(f"Error saving access request: '{exc}'")
            return None
        finally:
            con.close()

    def update_request_message_id(self, token: str, message_id: int) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute(
                "UPDATE requests SET message_id = ? WHERE token = ?",
                (
                    message_id,
                    token,
                ),
            )
            con.commit()
            return True if cur.rowcount > 0 else None
        except Exception as exc:
            logger.error(f"Error updating request message_id: '{exc}'")
            return False
        finally:
            con.close()

    def accept_mod_request(self, token: str) -> bool:
        data = self.get_mod_request(token)
        if not data or data["type"] != "mod":
            return False

        ok = self.add_board_mod(data["board_id"], data["target_id"])
        if not ok:
            pass

        deleted = self.delete_request(token)
        return deleted

    def delete_request(self, token: str) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute("DELETE FROM requests WHERE token = ?", (token,))
            con.commit()
            return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error deleting mod requesr: '{exc}'")
            return False
        finally:
            con.close()

    def add_board_mod(self, board_id: int, user_id: int) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute(
                "INSERT OR IGNORE INTO board_access (board_id, user_id) VALUES (?, ?)",
                (
                    board_id,
                    user_id,
                ),
            )
            con.commit()
            return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error adding board access: '{exc}'")
            return False
        finally:
            con.close()

    def get_token_by_message_id(self, chat_id: int, message_id: int) -> str | None:
        con, cur = self._create_con()
        try:
            cur.execute(
                "SELECT token FROM requests WHERE chat_id = ? AND message_id = ?",
                (
                    chat_id,
                    message_id,
                ),
            )
            res = cur.fetchone()
            return res["token"] if res else None
        except Exception as exc:
            logger.error(f"Error fetching token by message_id: '{exc}'")
            return None
        finally:
            con.close()

    def get_mod_request(self, token: str):
        con, cur = self._create_con()
        try:
            cur.execute("SELECT * FROM requests WHERE token = ?", (token,))
            return cur.fetchone()
        except Exception as exc:
            logger.error(f"Error fetching access request: '{exc}'")
            return None
        finally:
            con.close()

    def _create_con(self):
        con = get_connection()
        cur = con.cursor()
        return con, cur
