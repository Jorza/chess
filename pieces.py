# Pawn
# ~~Rook~~
# Knight
# ~~Bishop~~
# King
# ~~Queen~~


class Piece:
    def __init__(self, colour, x, y):
        self.x = self.validate_coord(x)
        self.y = self.validate_coord(y)
        self.colour = self.validate_colour(colour)
        self.valid_moves = []

    @staticmethod
    def validate_coord(coord):
        if not isinstance(coord, int):
            raise TypeError("Coordinate must be an integer.")
        if coord < 0 or coord > 7:
            raise ValueError("Coordinate value out of range.")
        return coord

    @staticmethod
    def validate_colour(colour):
        colour = colour.lower()
        if colour == 'w' or colour == 'white':
            return 'w'
        elif colour == 'b' or colour == 'black':
            return 'b'
        else:
            raise ValueError("Colour must either be white or black")


class RangedPiece(Piece):
    def __init__(self, colour, x, y):
        super().__init__(colour, x, y)

    def probe_path(self, board, update_func):
        x_probe, y_probe = update_func(self.x, self.y)
        try:
            while board[x_probe][y_probe] is None:
                self.valid_moves.append((x_probe, y_probe))
                x_probe, y_probe = update_func(x_probe, y_probe)
        except ValueError:
            # Reached end of board
            return
        # Current probed space is occupied
        if board[x_probe][y_probe].colour != self.colour:
            self.valid_moves.append((self.x, self.y))

    def update_higher_x(self, x, y):
        return self.validate_coord(x + 1), y

    def update_lower_x(self, x, y):
        return self.validate_coord(x - 1), y

    def update_higher_y(self, x, y):
        return x, self.validate_coord(y + 1)

    def update_lower_y(self, x, y):
        return x, self.validate_coord(y - 1)

    def update_higher_x_higher_y(self, x, y):
        return self.validate_coord(x + 1), self.validate_coord(y + 1)

    def update_lower_x_higher_y(self, x, y):
        return self.validate_coord(x - 1), self.validate_coord(y + 1)

    def update_higher_x_lower_y(self, x, y):
        return self.validate_coord(x + 1), self.validate_coord(y - 1)

    def update_lower_x_lower_y(self, x, y):
        return self.validate_coord(x - 1), self.validate_coord(y - 1)


class Rook(RangedPiece):
    def __init__(self, colour, x, y):
        super().__init__(colour, x, y)

    def get_valid_moves(self, board):
        self.probe_path(board, self.update_higher_x)
        self.probe_path(board, self.update_lower_x)
        self.probe_path(board, self.update_higher_y)
        self.probe_path(board, self.update_lower_y)


class Bishop(RangedPiece):
    def __init__(self, colour, x, y):
        super().__init__(colour, x, y)

    def get_valid_moves(self, board):
        self.probe_path(board, self.update_higher_x_higher_y)
        self.probe_path(board, self.update_lower_x_higher_y)
        self.probe_path(board, self.update_higher_x_lower_y)
        self.probe_path(board, self.update_lower_x_lower_y)


class Queen(RangedPiece):
    def __init__(self, colour, x, y):
        super().__init__(colour, x, y)

    def get_valid_moves(self, board):
        self.probe_path(board, self.update_higher_x)
        self.probe_path(board, self.update_lower_x)
        self.probe_path(board, self.update_higher_y)
        self.probe_path(board, self.update_lower_y)
        self.probe_path(board, self.update_higher_x_higher_y)
        self.probe_path(board, self.update_lower_x_higher_y)
        self.probe_path(board, self.update_higher_x_lower_y)
        self.probe_path(board, self.update_lower_x_lower_y)


class Pawn(Piece):
    def __init__(self, colour, x, y):
        super().__init__(colour, x, y)
        self.step = 1 if self.colour is 'w' else -1

    def get_valid_moves(self, board):
        valid_moves = []
        # No capture
        if board[self.x][self.y + self.step] is None:
            valid_moves.append((self.x, self.y + self.step))
            if board[self.x][self.y + 2*self.step] is None and (self.y - self.step) % 7 == 0:
                valid_moves.append((self.x, self.y + 2*self.step))

        # Capture right
        right_piece = board[self.x + 1][self.y + self.step]
        if right_piece is not None and right_piece.colour != self.colour:
                valid_moves.append((self.x + 1, self.y + self.step))

        # Capture left
        left_piece = board[self.x - 1][self.y + self.step]
        if left_piece is not None and left_piece.colour != self.colour:
                valid_moves.append((self.x - 1, self.y + self.step))
