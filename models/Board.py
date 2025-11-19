class Board:
    def __init__(self, owner_id: int, board_name: str, board_id: int = None):
        self.board_id = board_id
        self.board_name = board_name
        self.owner_id = owner_id

    def __repr__(self):
        return f"{self.__class__.__name__}(board_id={self.board_id}, board_name={self.board_name}, owner_id={self.owner_id})"
