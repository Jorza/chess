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

    def add_valid_move(self, x, y):
        check_after_move = self.board.is_check_after_move(self, x, y)
        if not check_after_move:
            self.valid_moves.append((x, y))

    def get_valid_moves(self):
        self.valid_moves.clear()
        self.get_moves_get_protected_squares()
        return self.valid_moves

    def get_protected_squares(self):
        # This is distinct from valid moves - eg: a piece can't move to a piece of the same colour, but does protect it.
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
                        self.add_valid_move(x_probe, y_probe)
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
                self.add_valid_move(x_probe, y_probe)

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
        self.has_moved = False

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
        if not protected_squares_flag:  # Only applies when looking for valid moves.
            if self.board.piece_grid[self.x][self.y + self.step] is None:
                self.add_valid_move(self.x, self.y + self.step)
                # Double-move if on starting rank
                if (self.y - self.step) % 7 == 0 and self.board.piece_grid[self.x][self.y + 2*self.step] is None:
                    self.add_valid_move(self.x, self.y + 2*self.step)

        # Capture right
        try:
            new_x, new_y = self.validate_coord(self.x + 1), self.validate_coord(self.y + self.step)
            if protected_squares_flag:
                self.protected_squares.append((new_x, new_y))
            else:
                right_piece = self.board.piece_grid[new_x][new_y]
                if right_piece is not None and right_piece.colour != self.colour:
                    self.add_valid_move(new_x, new_y)
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
                    self.add_valid_move(new_x, new_y)
        except ValueError:
            pass


class EnPassantPawn(Piece):
    def __init__(self, colour, x, y, board, piece_id, pawn_ref):
        super().__init__(colour, x, y, board, piece_id, "pawn")
        self.pawn = pawn_ref


class King(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id, "king")
        self.has_moved = False

    def get_opponent_protected_squares(self):
        protected_squares = []
        for piece in self.board.pieces[not self.colour]:
            if piece:
                protected_squares += piece.get_protected_squares()
        return protected_squares

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        if not protected_squares_flag:
            # If calculating valid_moves, find protected squares for all pieces of other colour ahead of time.
            opponent_protected_squares = self.get_opponent_protected_squares()

        # Regular moves
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
                        if not (new_x, new_y) in opponent_protected_squares:
                            self.valid_moves.append((new_x, new_y))

        # Castling
        # Conditions for castling:
        #     1. King must not have moved, King must not be in check
        #     For each rook:
        #         1. Rook must not have moved
        #         2. Squares between King and Rook must be empty
        #         3. Squares the King moves through (or to) must not be protected
        if not protected_squares_flag:
            # Only consider if calculating valid moves. Does not affect protected squares.
            if not self.has_moved and self.coords not in opponent_protected_squares:
                grid = self.board.piece_grid
                rank = 0 if self.colour else 7
                # King side
                king_rook = self.board.pieces[self.colour][15]
                if king_rook and not king_rook.has_moved:
                    if all(not grid[file][rank] and (file, rank) not in opponent_protected_squares for file in (5, 6)):
                        self.valid_moves.append((6, rank))
                # Queen side
                queen_rook = self.board.pieces[self.colour][8]
                if queen_rook and not queen_rook.has_moved:
                    if not grid[1][rank]:
                        if all(not grid[file][rank] and (file, rank) not in opponent_protected_squares for file in (2, 3)):
                            self.valid_moves.append((2, rank))

    def is_checked(self):
        protected_squares = self.get_opponent_protected_squares()
        return self.coords in protected_squares


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
                        self.add_valid_move(new_x, new_y)
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
                        self.add_valid_move(new_x, new_y)

