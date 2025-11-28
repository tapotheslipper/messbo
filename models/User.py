from datetime import datetime, timezone


class User:
    def __init__(
        self,
        tg_id: int,
        tg_username: str,
        id: int = None,
        created_at_utc: datetime = None,
        last_modified_at_utc: datetime = None,
    ):
        self.id = id
        self.tg_id = tg_id
        self.tg_username = tg_username

        if created_at_tc is None:
            self.created_at_utc = datetime.now(timezone.utc)
        else:
            self.created_at_utc = created_at_utc
        if last_modified_at_utc is None:
            self.last_modified_at_utc = datetime.now(timezone.utc)
        else:
            self.last_modified_at_utc = last_modified_at_utc

    def update_last_modified(self):
        self.last_modified_at_utc = datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, "
            f"tg_id={self.tg_id}, "
            f"tg_username={self.tg_username}, "
            f"created_at_utc={self.created_at_utc.isoformat()}, "
            f"last_modified_at_utc={self.last_modified_at_utc.isoformat()})"
        )
