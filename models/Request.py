from datetime import datetime, timezone


class Request:
    def __init__(
        self,
        token: str,
        chat_id: int,
        board_id: int,
        requester_id: int,
        target_id: int,
        message_id: int,
        type: str,
        created_at_utc: datetime = None,
    ):
        self.token = token
        self.chat_id = chat_id
        self.board_id = board_id
        self.requester_id = requester_id
        self.target_id = target_id
        self.message_id = message_id
        self.type = type
        self.created_at_utc = created_at_utc or datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(token={self.token}, "
            f"chat_id={self.chat_id}, "
            f"requester_id={self.requester_id}, "
            f"target_id={self.target_id}, "
            f"message_id={self.message_id}"
            f"type={self.type}, "
            f"created_at_utc={self.created_at_utc.isoformat()})"
        )
