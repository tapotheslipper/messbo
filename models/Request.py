from datetime import datetime, timezone


class Request:
    def __init__(
        self,
        chat_id: int,
        board_id: int,
        requester_id: int,
        target_id: int,
        type: str = "pending",
        id: int = None,
        created_at_utc: datetime = None,
    ):
        self.id = id
        self.chat_id = chat_id
        self.requester_id = requester_id
        self.target_id = target_id
        self.type = status

        if created_at_utc is None:
            self.created_at_utc = datetime.now(timezone.utc)
        else:
            self.created_at_utc = created_at_utc

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, "
            f"chat_id={self.chat_id}, "
            f"requester_id={self.requester_id}, "
            f"target_id={self.target_id}, "
            f"type={self.status}, "
            f"created_at_utc={self.created_at_utc.isoformat()})"
        )
