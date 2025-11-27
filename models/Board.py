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

        if created_at_utc is None:
            self.created_at_utc = datetime.now(timezone.utc)
        else:
            self.created_at_utc = created_at_utc
        if last_modified_at_utc is None:
            self.last_modified_at_utc = datetime.now(timezone.utc)
        else:
            self.last_modified_at_utc = last_modified_at_utc

    def set_name(self, new_name):
        self.name = new_name
        self.update_last_modified()

    def update_last_modified(self):
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
