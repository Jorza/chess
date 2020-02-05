# Rook
# Bishop
# Queen
# Pawn
# King
# Knight

# Rule - pieces cannot touch other pieces. They can check the board, but not modify anything else on it
#      - pieces do not implement how they capture other pieces

import pygame


class PieceSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Piece:
    def __init__(self, colour, x, y, board, piece_id, sprite_stem):
        self.colour = self.validate_colour(colour)  # 0 => white, 1 => black
        self.board = board
        # Each piece of a colour has a unique ID determined by its starting rank and file.
        # Pawns have IDs 0 through 7 for files 1 through 8 respectively.
        # Back row pieces have IDs 8 through 15 for files 1 through 8 respectively.
        # eg: Both Kings have an ID of 12.
        self.id = piece_id

        # Grid coordinates of the piece on the board. Integers 0 to 7 only
        self.x = self.validate_coord(x)
        self.y = self.validate_coord(y)

        self.valid_moves = []
        self.protected_squares = []

        colour_string = "b" if self.colour else "w"
        image_file = "assets/" + colour_string + "_" + sprite_stem + "_svg_NoShadow-svg.png"
        image = pygame.image.load(image_file).convert_alpha()
        self.sprite = PieceSprite(image, *self.pixel_coords)

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

    @property
    def coords(self):
        return self.x, self.y

    @property
    def pixel_coords(self):
        # Pixel coordinates relative to top-left corner of the display window.
        # Used for drawing sprites to the screen.
        return self.board.get_pixel_coords(self.x, self.y)

    def is_pinned(self):
        king = self.board.pieces[self.colour][12]
        opponent_pieces = self.board.pieces[not self.colour]
        opponent_ranged_pieces = (opponent_pieces[i] for i in (8, 10, 11, 13, 15) if opponent_pieces[i] is not None)

        # Check all opponent pieces that can pin
        for piece in opponent_ranged_pieces:
            # Check current piece is in between opponent piece and king
            if (piece.x <= self.x <= king.x or piece.x >= self.x >= king.x) and \
                    (piece.y <= self.y <= king.y or piece.y >= self.y >= king.y):
                # Once we know the above is satisfied, checking that the pieces are collinear is much easier.

                # Check pieces are collinear along a horizontal or vertical line
                rook_pin = piece.x == self.x == king.x or piece.y == self.y == king.y
                # Check pieces are collinear along a line of gradient 1 or -1.
                bishop_pin = abs(piece.x - self.x) == abs(piece.y - self.y) and \
                    abs(king.x - self.x) == abs(king.y - self.y)

                if (piece.id == 8 or piece.id == 15) and rook_pin or \
                        (piece.id == 10 or piece.id == 13) and bishop_pin or \
                        piece.id == 11 and (bishop_pin or rook_pin):
                    return True
        return False

    def get_valid_moves(self):
        self.valid_moves.clear()
        # Check if piece is pinned. If so, it cannot be moved. Leave the list of valid moves empty
        if not self.is_pinned():
            self.get_moves_get_protected_squares()
        return self.valid_moves

    def get_protected_squares(self):
        # This is distinct from valid moves - a piece can not move to a piece of the same colour, but does protect it.
        # Necessary for detecting where the Kings can move so they don't move into check.
        self.protected_squares.clear()
        self.get_moves_get_protected_squares(protected_squares_flag=True)
        return self.protected_squares

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        # Inherit and overwrite this method.
        pass


class RangedPiece(Piece):
    def __init__(self, colour, x, y, board, piece_id, sprite_stem):
        super().__init__(colour, x, y, board, piece_id, sprite_stem)

    def probe_path(self, update_func, protected_squares_flag=False):
        try:
            # Get next space on path
            x_probe, y_probe = update_func(self.x, self.y)
            probe_piece = self.board.piece_grid[x_probe][y_probe]
            # Probe as long as the path is not blocked.
            # Also probe if the path is blocked by the opponent's King. This allows ranged pieces to protect squares
            # beyond the King, and prevents the King from being able to stay in check if it moves.
            while probe_piece is None or (isinstance(probe_piece, King) and probe_piece.colour != self.colour):
                if protected_squares_flag:
                    self.protected_squares.append((x_probe, y_probe))
                if not protected_squares_flag:
                    if probe_piece is None:
                        self.valid_moves.append((x_probe, y_probe))
                    else:
                        break  # If looking for valid moves, any piece blocks the path - including the opponent's King.
                x_probe, y_probe = update_func(x_probe, y_probe)
                probe_piece = self.board.piece_grid[x_probe][y_probe]
        except ValueError:
            # Reached edge of board
            return
        # Current probed space is occupied. Space is protected, may be able to move to the space by capturing.
        if protected_squares_flag:
            self.protected_squares.append((x_probe, y_probe))
        else:
            if probe_piece.colour != self.colour:
                self.valid_moves.append((x_probe, y_probe))

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
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "rook")

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        self.probe_path(self.update_higher_x, protected_squares_flag)
        self.probe_path(self.update_lower_x, protected_squares_flag)
        self.probe_path(self.update_higher_y, protected_squares_flag)
        self.probe_path(self.update_lower_y, protected_squares_flag)


class Bishop(RangedPiece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "bishop")

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        self.probe_path(self.update_higher_x_higher_y, protected_squares_flag)
        self.probe_path(self.update_lower_x_higher_y, protected_squares_flag)
        self.probe_path(self.update_higher_x_lower_y, protected_squares_flag)
        self.probe_path(self.update_lower_x_lower_y, protected_squares_flag)


class Queen(RangedPiece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "queen")

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        self.probe_path(self.update_higher_x, protected_squares_flag)
        self.probe_path(self.update_lower_x, protected_squares_flag)
        self.probe_path(self.update_higher_y, protected_squares_flag)
        self.probe_path(self.update_lower_y, protected_squares_flag)
        self.probe_path(self.update_higher_x_higher_y, protected_squares_flag)
        self.probe_path(self.update_lower_x_higher_y, protected_squares_flag)
        self.probe_path(self.update_higher_x_lower_y, protected_squares_flag)
        self.probe_path(self.update_lower_x_lower_y, protected_squares_flag)


class Pawn(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "pawn")
        self.step = 1 if self.colour else -1

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        # Straight movement
        if self.board.piece_grid[self.x][self.y + self.step] is None:
            self.valid_moves.append((self.x, self.y + self.step))
            # Double-move if on starting rank
            if (self.y - self.step) % 7 == 0 and self.board.piece_grid[self.x][self.y + 2*self.step] is None:
                self.valid_moves.append((self.x, self.y + 2*self.step))

        # Capture right
        try:
            new_x, new_y = self.validate_coord(self.x + 1), self.validate_coord(self.y + self.step)
            if protected_squares_flag:
                self.protected_squares.append((new_x, new_y))
            else:
                right_piece = self.board.piece_grid[new_x][new_y]
                if right_piece is not None and right_piece.colour != self.colour:
                    self.valid_moves.append((new_x, new_y))
        except ValueError:
            pass

        # Capture left
        try:
            new_x, new_y = self.validate_coord(self.x - 1), self.validate_coord(self.y + self.step)
            if protected_squares_flag:
                self.protected_squares.append((new_x, new_y))
            else:
                left_piece = self.board.piece_grid[new_x][new_y]
                if left_piece is not None and left_piece.colour != self.colour:
                    self.valid_moves.append((new_x, new_y))
        except ValueError:
            pass


class EnPassantPawn(Piece):
    def __init__(self, colour, x, y, board, piece_id, pawn_ref):
        super().__init__(colour, x, y, board, piece_id, "pawn")
        self.pawn = pawn_ref


class King(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "king")

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        if not protected_squares_flag:
            # If calculating valid_moves, find protected squares for all pieces of other colour ahead of time.
            current_protected_squares = []
            for piece in self.board.pieces[not self.colour]:
                if piece:
                    current_protected_squares += piece.get_protected_squares()

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
                if protected_squares_flag:
                    self.protected_squares.append((new_x, new_y))
                else:
                    new_space = self.board.piece_grid[new_x][new_y]
                    if new_space is None or new_space.colour != self.colour:
                        if not (new_x, new_y) in current_protected_squares:
                            self.valid_moves.append((new_x, new_y))

    def is_checked(self):
        for piece in self.board.pieces[not self.colour]:
            if piece:
                if self.coords in piece.get_protected_squares():
                    return True
        return False


class Knight(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "knight")

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        self.valid_moves.clear()
        for delta_x in [-2, 2]:
            new_x = self.x + delta_x
            try:
                self.validate_coord(new_x)
            except ValueError:
                continue

            for delta_y in [-1, 1]:
                new_y = self.y + delta_y
                try:
                    self.validate_coord(new_y)
                except ValueError:
                    continue

                if protected_squares_flag:
                    self.protected_squares.append((new_x, new_y))
                else:
                    new_space = self.board.piece_grid[new_x][new_y]
                    if new_space is None or new_space.colour != self.colour:
                        self.valid_moves.append((new_x, new_y))
        for delta_y in [-2, 2]:
            new_y = self.y + delta_y
            try:
                self.validate_coord(new_y)
            except ValueError:
                continue

            for delta_x in [-1, 1]:
                new_x = self.x + delta_x
                try:
                    self.validate_coord(new_x)
                except ValueError:
                    continue

                if protected_squares_flag:
                    self.protected_squares.append((new_x, new_y))
                else:
                    new_space = self.board.piece_grid[new_x][new_y]
                    if new_space is None or new_space.colour != self.colour:
                        self.valid_moves.append((new_x, new_y))

