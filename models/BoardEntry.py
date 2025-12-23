from datetime import datetime, timezone


class BoardEntry:
    def __init__(
        self,
        board_id: int,
        user_id: int,
        content: str,
        local_id: int = None,
        id: int = None,
        created_at_utc: datetime = None,
        last_modified_at_utc: datetime = None,
    ):
        self.id = id
        self.board_id = board_id
        self.local_id = local_id
        self.user_id = user_id
        self.content = content

        self.created_at_utc = created_at_utc or datetime.now(timezone.utc)
        self.last_modified_at_utc = last_modified_at_utc or datetime.now(timezone.utc)

    def set_content(self, new_content: str):
        self.content = new_content
        self._update_last_modified()

    def _update_last_modified(self):
        self.last_modified_at_utc = datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"id={self.id}, "
            f"board_id={self.board_id}, "
            f"local_id={self.local_id}, "
            f"user_id={self.user_id}, "
            f"content={self.content[:10]}..., "
            f"created_at_utc={self.created_at_utc.isoformat()}, "
            f"last_modified_at_utc={self.last_modified_at_utc.isoformat()})"
        )
