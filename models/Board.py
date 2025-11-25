from datetime import datetime, timezone

class Board:
    def __init__(
        self,
        owner_id: int,
        board_name: str,
        board_id: int = None
    ):
        self.id = board_id
        self.name = board_name
        self.owner_id = owner_id

        self.created_at_utc = datetime.now(timezone.utc).isoformat()
        self.last_modified_at_utc = self.created_at_utc

    def set_name(self, new_name):
        self.name = new_name
        self.update_last_modified()

    def update_last_modified(self):
        self.last_modified_at_utc = datetime.now(timezone.utc).isoformat()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, "
            f"name={self.name}, "
            f"owner_id={self.owner_id}, "
            f"created_at_utc={self.created_at_utc}, "
            f"last_modified_at_utc={self.last_modified_at_utc})"
        )
