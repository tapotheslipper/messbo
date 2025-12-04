from datetime import datetime, timezone


class Board:
    def __init__(
        self,
        name: str,
        owner_id: int,
        chat_id: int,
        id: int = None,
        created_at_utc: datetime = None,
        last_modified_at_utc: datetime = None,
    ):
        self.id = id
        self.name = name
        self.chat_id = chat_id
        self.owner_id = owner_id

        self.created_at_utc = created_at_utc or datetime.now(timezone.utc)
        self.last_modified_at_utc = last_modified_at_utc or datetime.now(timezone.utc)

    def set_name(self, new_name):
        self.name = new_name
        self._update_last_modified()

    def _update_last_modified(self):
        self.last_modified_at_utc = datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, "
            f"name={self.name}, "
            f"owner_id={self.owner_id}, "
            f"created_at_utc={self.created_at_utc.isoformat()}, "
            f"last_modified_at_utc={self.last_modified_at_utc.isoformat()})"
        )
