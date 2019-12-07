# ~~Rook~~
# ~~Bishop~~
# ~~Queen~~
# ~~Pawn~~
# ~~King~~
# ~~Knight~~

# Rule - pieces cannot touch other pieces. They can check the board, but not modify anything on it
#      - pieces do not implement how they capture other pieces
# Piece.sprite = <PieceSprite object>

import pygame


class PieceSprite(pygame.sprite.Sprite):
    def __init__(self, rect, image, mask):
        super().__init__()
        self.rect = rect
        self.image = image
        self.mask = mask


class Piece:
    def __init__(self, colour, x, y, board_ref):
        self.x = self.validate_coord(x)
        self.y = self.validate_coord(y)
        self.colour = self.validate_colour(colour)  # 0 => white, 1 => black
        self.Board = board_ref
        self.valid_moves = []
        self.sprite = None

    @staticmethod
    def validate_coord(coord):
        if not isinstance(coord, int):
            raise TypeError("Coordinate must be an integer.")
        if coord < 0 or coord > 7:
            raise ValueError("Coordinate value out of range.")
        return coord

    @staticmethod
    def validate_colour(colour):
        if colour < 0 or colour > 1:
            raise ValueError("Colour must either be 0 (white) or 1 (black)")
        return colour

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
            while self.Board.board[x_probe][y_probe] is None:
                self.valid_moves.append((x_probe, y_probe))
                x_probe, y_probe = update_func(x_probe, y_probe)
        except ValueError:
            # Reached end of self.Board.board
            return
        # Current probed space is occupied
        if self.Board.board[x_probe][y_probe].colour != self.colour:
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
        #self.sprite = Sprite

    def get_valid_moves(self):
        self.valid_moves.clear()
        self.probe_path(self.update_higher_x)
        self.probe_path(self.update_lower_x)
        self.probe_path(self.update_higher_y)
        self.probe_path(self.update_lower_y)


class Bishop(RangedPiece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)
        #self.sprite = Sprite

    def get_valid_moves(self):
        self.valid_moves.clear()
        self.probe_path(self.update_higher_x_higher_y)
        self.probe_path(self.update_lower_x_higher_y)
        self.probe_path(self.update_higher_x_lower_y)
        self.probe_path(self.update_lower_x_lower_y)


class Queen(RangedPiece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)
        # self.sprite = Sprite

    def get_valid_moves(self):
        self.valid_moves.clear()
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
        # self.sprite = Sprite
        self.step = 1 if self.colour else -1

    def get_valid_moves(self):
        self.valid_moves.clear()
        # Straight movement
        if self.Board.board[self.x][self.y + self.step] is None:
            self.valid_moves.append((self.x, self.y + self.step))
            # Double-move if on starting rank
            if self.Board.board[self.x][self.y + 2*self.step] is None and (self.y - self.step) % 7 == 0:
                self.valid_moves.append((self.x, self.y + 2*self.step))

        # Capture right
        try:
            new_x, new_y = self.validate_coord(self.x + 1), self.validate_coord(self.y + self.step)
            right_piece = self.Board.board[new_x][new_y]
            if right_piece is not None and right_piece.colour != self.colour:
                self.valid_moves.append((new_x, new_y))
        except ValueError:
            pass

        # Capture left
        try:
            new_x, new_y = self.validate_coord(self.x - 1), self.validate_coord(self.y + self.step)
            left_piece = self.Board.board[new_x][new_y]
            if left_piece is not None and left_piece.colour != self.colour:
                self.valid_moves.append((new_x, new_y))
        except ValueError:
            pass


class EnPassantPawn(Piece):
    def __init__(self, colour, x, y, board_ref, pawn_ref):
        super().__init__(colour, x, y, board_ref)
        self.pawn = pawn_ref


class King(Piece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)
        # self.sprite = Sprite

    def get_valid_moves(self):
        self.valid_moves.clear()
        for delta_x in [-1, 0, 1]:
            try:
                self.validate_coord(self.x + delta_x)
            except ValueError:
                continue

            for delta_y in [-1, 0, 1]:
                try:
                    self.validate_coord(self.y + delta_y)
                except ValueError:
                    continue
                if delta_x == 0 and delta_y == 0:
                    continue

                new_x, new_y = self.x + delta_x, self.y + delta_y
                new_space = self.Board.board[new_x, new_y]
                if new_space is None or new_space.colour != self.colour:
                    if not self.Board.is_attacked(new_x, new_y, ~self.colour):
                        self.valid_moves.append((new_x, new_y))


class Knight(Piece):
    def __init__(self, colour, x, y, board_ref):
        super().__init__(colour, x, y, board_ref)
        # self.sprite = Sprite

    def get_valid_moves(self):
        self.valid_moves.clear()
        for delta_x in [-2, 2]:
            try:
                self.validate_coord(self.x + delta_x)
            except ValueError:
                continue

            for delta_y in [-1, 1]:
                try:
                    self.validate_coord(self.y + delta_y)
                except ValueError:
                    continue

                new_x, new_y = self.x + delta_x, self.y + delta_y
                new_space = self.Board.board[new_x, new_y]
                if new_space is None or new_space.colour != self.colour:
                    self.valid_moves.append((new_x, new_y))

                # Horse can also move 2 in y-direction followed by 1 in x-direction.
                # Is equivalent to above, but with x and y switched.
                new_space = self.Board.board[new_y, new_x]
                if new_space is None or new_space.colour != self.colour:
                    self.valid_moves.append((new_y, new_x))
