# Rook
# Bishop
# Queen
# Pawn
# King
# Knight

# Rule - pieces cannot touch other pieces. They can check the board, but not modify anything on it
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
    def __init__(self, colour, x, y, board, piece_id):
        self.colour = self.validate_colour(colour)  # 0 => white, 1 => black
        self.board = board
        self.id = piece_id

        # Grid coordinates of the piece on the board. Integers 0 to 7 only
        self.x = self.validate_coord(x)
        self.y = self.validate_coord(y)

        self.valid_moves = []
        self.protected_squares = []
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

    @property
    def pixel_coords(self):
        # Pixel coordinates relative to top-left corner of the display window.
        # Used for drawing sprites to the screen.
        return self.board.get_pixel_coords(self.x, self.y)

    def get_valid_moves(self):
        self.valid_moves.clear()
        self.get_moves_get_protected_squares()

    def get_protected_squares(self):
        self.protected_squares.clear()
        self.get_moves_get_protected_squares(protected_squares_flag=True)

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        pass


class RangedPiece(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id)

    def probe_path(self, update_func, protected_squares_flag=False):
        try:
            # Get next space on path
            x_probe, y_probe = update_func(self.x, self.y)
            # Continue probing along path while spaces are empty
            while self.board.piece_grid[x_probe][y_probe] is None:
                if protected_squares_flag:
                    self.protected_squares.append((x_probe, y_probe))
                else:
                    self.valid_moves.append((x_probe, y_probe))
                x_probe, y_probe = update_func(x_probe, y_probe)
        except ValueError:
            # Reached edge of board
            return
        # Current probed space is occupied
        if protected_squares_flag:
            self.protected_squares.append((x_probe, y_probe))
        else:
            if self.board.piece_grid[x_probe][y_probe].colour != self.colour:
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
        super().__init__(colour, x, y, board, piece_id)

        image_white = pygame.image.load("assets/w_rook_svg_NoShadow-svg.png").convert_alpha()
        image_black = pygame.image.load("assets/b_rook_svg_NoShadow-svg.png").convert_alpha()
        image = image_white if not self.colour else image_black
        self.sprite = PieceSprite(image, *self.pixel_coords)

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        self.probe_path(self.update_higher_x, protected_squares_flag)
        self.probe_path(self.update_lower_x, protected_squares_flag)
        self.probe_path(self.update_higher_y, protected_squares_flag)
        self.probe_path(self.update_lower_y, protected_squares_flag)


class Bishop(RangedPiece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id)

        image_white = pygame.image.load("assets/w_bishop_svg_NoShadow-svg.png").convert_alpha()
        image_black = pygame.image.load("assets/b_bishop_svg_NoShadow-svg.png").convert_alpha()
        image = image_white if not self.colour else image_black
        self.sprite = PieceSprite(image, *self.pixel_coords)

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
        self.probe_path(self.update_higher_x_higher_y, protected_squares_flag)
        self.probe_path(self.update_lower_x_higher_y, protected_squares_flag)
        self.probe_path(self.update_higher_x_lower_y, protected_squares_flag)
        self.probe_path(self.update_lower_x_lower_y, protected_squares_flag)


class Queen(RangedPiece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id)

        image_white = pygame.image.load("assets/w_queen_svg_NoShadow-svg.png").convert_alpha()
        image_black = pygame.image.load("assets/b_queen_svg_NoShadow-svg.png").convert_alpha()
        image = image_white if not self.colour else image_black
        self.sprite = PieceSprite(image, *self.pixel_coords)

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
        super().__init__(colour, x, y, board, piece_id)

        image_white = pygame.image.load("assets/w_pawn_svg_NoShadow-svg.png").convert_alpha()
        image_black = pygame.image.load("assets/b_pawn_svg_NoShadow-svg.png").convert_alpha()
        image = image_white if not self.colour else image_black
        self.sprite = PieceSprite(image, *self.pixel_coords)
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
        super().__init__(colour, x, y, board, piece_id)
        self.pawn = pawn_ref


class King(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id)

        image_white = pygame.image.load("assets/w_king_svg_NoShadow-svg.png").convert_alpha()
        image_black = pygame.image.load("assets/b_king_svg_NoShadow-svg.png").convert_alpha()
        image = image_white if not self.colour else image_black
        self.sprite = PieceSprite(image, *self.pixel_coords)

    def get_moves_get_protected_squares(self, protected_squares_flag=False):
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
                        if not self.board.is_attacked(new_x, new_y, not self.colour):
                            self.valid_moves.append((new_x, new_y))


class Knight(Piece):
    def __init__(self, colour, x, y, board, piece_id):
        super().__init__(colour, x, y, board, piece_id)

        image_white = pygame.image.load("assets/w_knight_svg_NoShadow-svg.png").convert_alpha()
        image_black = pygame.image.load("assets/b_knight_svg_NoShadow-svg.png").convert_alpha()
        image = image_white if not self.colour else image_black
        self.sprite = PieceSprite(image, *self.pixel_coords)

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
