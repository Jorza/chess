class Board:
    def __init__(self):
        self.board = self.get_grid(8, 8)
        self.pieces = [], []  # pieces[0] => white pieces, pieces[1] => black pieces

    @staticmethod
    def get_grid(m, n):
        grid = []
        for i in range(m):
            grid.append([None] * n)
        return grid

    def is_attacked(self, x, y, colour):
        for piece in self.pieces[colour]:
            piece.get_valid_moves()
            if (x, y) in piece.valid_moves:
                return piece
        return False
