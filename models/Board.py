class Board:
    def __init__(self, owner_id: int, board_name: str, board_id: int = None):
        self.id = board_id
        self.name = board_name
        self.owner_id = owner_id

    def __repr__(self):
        return (f"{self.__class__.__name__}"
            f"(id={self.id}, "
            f"name={self.name}, "
            f"owner_id={self.owner_id})")
