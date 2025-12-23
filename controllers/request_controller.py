from database import get_connection
from models import Logger, Request
from datetime import datetime, timezone
import sqlite3
import uuid

logger = Logger().get_logger()


class RequestController:
    def __init__(self):
        pass

    def _create_con(self):
        con = get_connection()
        cur = con.cursor()
        return con, cur

    def _save_request(
        self,
        chat_id: int,
        board_id: int,
        requester_id: int,
        target_id: int,
        message_id: int,
        req_type: str,
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
                type=req_type,
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
            logger.error(f"Error saving {req_type} request: '{exc}'")
            return None
        finally:
            con.close()

    def add_mod_request(
        self,
        chat_id: int,
        board_id: int,
        requester_id: int,
        target_id: int,
        message_id: int,
    ) -> str | None:
        return self._save_request(
            chat_id, board_id, requester_id, target_id, message_id, "mod"
        )

    def add_own_request(
        self,
        chat_id: int,
        board_id: int,
        requester_id: int,
        target_id: int,
        message_id: int,
    ) -> str | None:
        return self._save_request(
            chat_id, board_id, requester_id, target_id, message_id, "own"
        )

    def accept_mod_request(self, token: str) -> bool:
        data = self.get_request_details(token)
        if not data or data["type"] != "mod":
            return False

        self.add_board_mod(data["board_id"], data["target_id"])
        return self.delete_request(token)

    def accept_own_request(self, token: str) -> bool:
        data = self.get_request_details(token)
        if not data or data["type"] != "own":
            return False

        con, cur = self._create_con()
        try:
            cur.execute(
                "UPDATE boards SET owner_id = ? WHERE id = ?",
                (data["target_id"], data["board_id"]),
            )
            cur.execute(
                "INSERT OR IGNORE INTO board_access (board_id, user_id) VALUES (?, ?)",
                (data["board_id"], data["target_id"]),
            )

            con.commit()
            return self.delete_request(token)
        except Exception as exc:
            logger.error(f"Error accepting ownership request: '{exc}'")
            return False
        finally:
            con.close()

    def remove_mod(self, board_id: int, user_id: int) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute(
                "DELETE FROM board_access WHERE board_id = ? AND user_id = ?",
                (board_id, user_id),
            )
            con.commit()
            return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error removing board access: '{exc}'")
            return False
        finally:
            con.close()

    def delete_request(self, token: str) -> bool:
        con, cur = self._create_con()
        try:
            cur.execute("DELETE FROM requests WHERE token = ?", (token,))
            con.commit()
            return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error deleting request: '{exc}'")
            return False
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
            return cur.rowcount > 0
        except Exception as exc:
            logger.error(f"Error updating request message_id: '{exc}'")
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

    def get_request_details(self, token: str):
        con, cur = self._create_con()
        try:
            cur.execute("SELECT * FROM requests WHERE token = ?", (token,))
            return cur.fetchone()
        except Exception as exc:
            logger.error(f"Error fetching request details: '{exc}'")
            return None
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
