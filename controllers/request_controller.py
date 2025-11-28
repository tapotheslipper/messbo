from database import get_connection
from models import Logger, Request
from datetime import datetime, timezone
import sqlite3

logger = Logger().get_logger()


class RequestController:
    def __init__(self):
        pass

    def save_access_request(
        self, chat_id: int, board_id: int, requester_id: int, target_id: int
    ) -> int | None:
        con = self._create_con()
        cur = self._create_cur()
        created_at = last_modified_at = datetime.utcnow().isoformat()
        try:
            cur.execute(
                "INSERT INTO access_requests (chat_id, board_id, requester_id, target_id, status, created_at_utc, last_modified_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    chat_id,
                    board_id,
                    requester_id,
                    target_id,
                    "pending",
                    created_at,
                    last_modified_at,
                ),
            )
            con.commit()
            return cur.lastrowid
        except Exception as exc:
            logger.error(f"Error saving access request: '{exc}'")
            return None
        finally:
            con.close()

    def get_access_request(self, request_id: int):
        con = self._create_con()
        cur = self._create_cur()
        try:
            cur.execute(
                "SELECT * FROM access_requests WHERE request_id = ?", (request_id,)
            )
            return cur.fetchone()
        except Exception as exc:
            logger.error(f"Error fetching access request: '{exc}'")
            return None
        finally:
            con.close()

    def _create_con(self):
        return get_connection()

    def _create_cur(self, connection):
        return connection.cursor()
