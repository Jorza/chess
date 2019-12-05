# ~~Rook~~
# ~~Bishop~~
# ~~Queen~~
# Pawn
#  - Add en passant capturing
# Knight
# King


class Piece:
    def __init__(self, colour, x, y, board_ref):
        self.x = self.validate_coord(x)
        self.y = self.validate_coord(y)
        self.colour = self.validate_colour(colour)
        self.board = board_ref
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

    def get_valid_moves(self):
        pass

    def move(self, x, y):
        if not self.valid_moves:
            self.get_valid_moves()
        if (x, y) in self.valid_moves:
            self.x = x
            self.y = y
            self.valid_moves.clear()


class RangedPiece(Piece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)

    def probe_path(self, update_func):
        try:
            # Get next space on path
            x_probe, y_probe = update_func(self.x, self.y)
            # Continue probing along path while spaces are empty
            while self.board[x_probe][y_probe] is None:
                self.valid_moves.append((x_probe, y_probe))
                x_probe, y_probe = update_func(x_probe, y_probe)
        except ValueError:
            # Reached end of self.board
            return
        # Current probed space is occupied
        if self.board[x_probe][y_probe].colour != self.colour:
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
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)

    def get_valid_moves(self):
        self.probe_path(self.update_higher_x)
        self.probe_path(self.update_lower_x)
        self.probe_path(self.update_higher_y)
        self.probe_path(self.update_lower_y)


class Bishop(RangedPiece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)

    def get_valid_moves(self):
        self.probe_path(self.update_higher_x_higher_y)
        self.probe_path(self.update_lower_x_higher_y)
        self.probe_path(self.update_higher_x_lower_y)
        self.probe_path(self.update_lower_x_lower_y)


class Queen(RangedPiece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)

    def get_valid_moves(self):
        self.probe_path(self.update_higher_x)
        self.probe_path(self.update_lower_x)
        self.probe_path(self.update_higher_y)
        self.probe_path(self.update_lower_y)
        self.probe_path(self.update_higher_x_higher_y)
        self.probe_path(self.update_lower_x_higher_y)
        self.probe_path(self.update_higher_x_lower_y)
        self.probe_path(self.update_lower_x_lower_y)


class Pawn(Piece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)
        self.step = 1 if self.colour is 'w' else -1

    def get_valid_moves(self):
        valid_moves = []
        # Straight movement
        if self.board[self.x][self.y + self.step] is None:
            valid_moves.append((self.x, self.y + self.step))
            # Double-move if on starting rank
            if self.board[self.x][self.y + 2*self.step] is None and (self.y - self.step) % 7 == 0:
                valid_moves.append((self.x, self.y + 2*self.step))

        # Capture right
        right_piece = self.board[self.x + 1][self.y + self.step]
        if right_piece is not None and right_piece.colour != self.colour:
                valid_moves.append((self.x + 1, self.y + self.step))

        # Capture left
        left_piece = self.board[self.x - 1][self.y + self.step]
        if left_piece is not None and left_piece.colour != self.colour:
                valid_moves.append((self.x - 1, self.y + self.step))
