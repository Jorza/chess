import pygame
import exceptions
import pieces


class Board:
    def __init__(self):
        self.tile_size = 65
        self.x_offset = 200
        self.y_offset = 100

        self.tiles = pygame.image.load("assets/board-tiles.png").convert()
        self.labels_white = pygame.image.load("assets/board-white-labels.png").convert_alpha()
        self.labels_black = pygame.image.load("assets/board-black-labels.png").convert_alpha()

        self.moves_overlay = self.get_surface(self.tile_size, self.tile_size, (0, 204, 0), 80)
        self.check_overlay = self.get_surface(self.tile_size, self.tile_size, (204, 204, 0), 80)

        self.pawn_promotions_white = pygame.image.load("assets/w_pawn_promotions.png").convert_alpha()
        self.pawn_promotions_black = pygame.image.load("assets/b_pawn_promotions.png").convert_alpha()

        self.piece_grid = self.get_grid(8, 8)

        # Bitlists for pieces active in the game (not captured).
        # Each piece has an ID (piece.id) which gives its position in the list. The pawns have IDs 0 - 7 going from file
        # 1 to file 8 (x = 0 to x = 7). The back pieces are numbered similarly, but with 8 - 15.
        # The IDs for corresponding white and black pieces are the same (eg: White King == Black King == 12).
        # pieces[0] => white pieces, pieces[1] => black pieces
        self.pieces = [None] * 16, [None] * 16

        # Bitlist for an en-passant pawn of each colour. index 0 => white, index 1 => black.
        # Only one may exist for each colour at a time. Must be cleared after the opponent's turn.
        self.en_passant_pawns = [None, None]

        # Groups to quickly draw pieces of each colour
        # piece_sprites[0] => white sprites, piece_sprites[1] => black sprites
        self.piece_sprites = pygame.sprite.Group(), pygame.sprite.Group()

        self.set_pieces()

    @staticmethod
    def get_grid(m, n):
        grid = []
        for i in range(m):
            grid.append([None] * n)
        return grid

    @staticmethod
    def get_surface(width, height, colour, alpha):
        surface = pygame.Surface((width, height))
        surface.fill(colour)
        surface.set_alpha(alpha)
        return surface

    def get_board_coords(self, x, y):
        x, y = (x - self.x_offset) // self.tile_size, (y - self.y_offset) // self.tile_size
        if x < 0 or x > 7 or y < 0 or y > 7:
            raise ValueError("Coordinates are not on the board")
        return x, y

    def get_pixel_coords(self, x, y):
        # Pixel coordinates relative to top-left corner of the display window.
        return x * self.tile_size + self.x_offset, y * self.tile_size + self.y_offset

    def add_piece_sprite(self, piece):
        self.piece_sprites[piece.colour].add(piece.sprite)

    def create_piece_on_board(self, piece_class, colour, file, rank, piece_id=None, pawn=None):
        if piece_class == pieces.EnPassantPawn:
            assert pawn is not None
            piece = piece_class(colour, file, rank, self, pawn)
            self.en_passant_pawns[colour] = piece
        else:
            piece = piece_class(colour, file, rank, self, piece_id)
            self.pieces[colour][piece_id] = piece
            self.add_piece_sprite(piece)
        self.piece_grid[file][rank] = piece

    def remove_expired_en_passant_pawn(self, colour):
        ep_pawn = self.en_passant_pawns[colour]
        self.en_passant_pawns[colour] = None

        pawn_space = self.piece_grid[ep_pawn.x][ep_pawn.y]
        if isinstance(pawn_space, pieces.EnPassantPawn):
            self.piece_grid[ep_pawn.x][ep_pawn.y] = None

    def set_pieces(self):
        # Create pieces in starting position on the board.
        # Add pieces to bitlists for each colour, add to piece_grid, add sprites to groups.

        piece_classes = [pieces.Rook, pieces.Knight, pieces.Bishop, pieces.Queen,
                         pieces.King, pieces.Bishop, pieces.Knight, pieces.Rook]
        for colour in [0, 1]:
            pawn_rank = 1 if colour else 6
            back_rank = 0 if colour else 7
            for file in range(8):
                # Pawns
                self.create_piece_on_board(pieces.Pawn, colour, file, pawn_rank, file)
                # Back row pieces
                self.create_piece_on_board(piece_classes[file], colour, file, back_rank, file + 8)

    def capture(self, piece, capturing_piece):
        if isinstance(piece, pieces.EnPassantPawn):
            if isinstance(capturing_piece, pieces.Pawn):
                # Remove en-passant pawn
                self.en_passant_pawns[piece.colour] = None

                # Capture pawn
                piece = piece.pawn
                self.capture(piece, None)
                # No need to pass capturing_piece, since it is guaranteed that 'piece' won't be another EnPassantPawn.
                # Must remove captured pawn from piece_grid manually, since nothing will move to take its place.
                self.piece_grid[piece.x][piece.y] = None
        else:
            self.pieces[piece.colour][piece.id] = None
            piece.sprite.kill()
        # Don't need to remove piece off piece_grid, since it will be replaced when the capturing piece is moved.

    def move(self, piece, x, y):
        pieces.Piece.validate_coord(x)
        pieces.Piece.validate_coord(y)

        # If the piece is a pawn...
        if isinstance(piece, pieces.Pawn):
            # ...and is making a double-move, create an en-passant pawn
            if abs(y - piece.y) > 1:
                piece_class, colour, file, rank = pieces.EnPassantPawn, piece.colour, piece.x, piece.y + piece.step
                self.create_piece_on_board(piece_class, colour, file, rank, pawn=piece)

            # ...and is on the second-back rank (so it will be moved to the back rank), promote it.
            elif (piece.y - 6 * piece.step) % 7 == 0:
                raise exceptions.PawnPromotionError(piece, x, y)

        # If the piece is a Rook, mark it as having moved
        if isinstance(piece, pieces.Rook) and not piece.has_moved:
            piece.has_moved = True

        # If the piece is a King, mark it as having moved. Handle castling
        if isinstance(piece, pieces.King) and not piece.has_moved:
            piece.has_moved = True
            if abs(x - piece.x) > 1:
                rook_initial_file = 0 if x < piece.x else 7
                rook_final_file = 3 if x < piece.x else 5
                rook = self.pieces[piece.colour][rook_initial_file + 8]
                self.move(rook, rook_final_file, y)

        captured_piece = self.piece_grid[x][y]
        if captured_piece:
            self.capture(captured_piece, piece)

        self.piece_grid[piece.x][piece.y] = None
        self.piece_grid[x][y] = piece
        piece.x, piece.y = x, y
        piece.sprite.rect.x, piece.sprite.rect.y = self.get_pixel_coords(x, y)

    def promote(self, pawn_promotion, promotion_piece):
        pawn, x, y = pawn_promotion.properties
        possible_promotions = pieces.Queen, pieces.Rook, pieces.Bishop, pieces.Knight
        assert promotion_piece in possible_promotions

        captured_piece = self.piece_grid[x][y]
        if captured_piece:
            self.capture(captured_piece, pawn)

        # Remove old pawn
        self.piece_grid[pawn.x][pawn.y] = None
        # Don't need to kill sprite, as it was already done when the pawn was picked up

        # Create new piece, replace position of old pawn in self.pieces
        self.create_piece_on_board(promotion_piece, pawn.colour, x, y, pawn.id)

    def is_check(self, colour):
        # This is used internally when checking valid moves so they do not leave the King in check.
        king = self.pieces[colour][12]
        return king.is_checked()

    def is_check_or_checkmate(self, colour):
        # This may be used when running the game.
        check = self.is_check(colour)
        if all(not piece.get_valid_moves() for piece in self.pieces[colour] if piece):
            # No moves left
            if check:
                raise exceptions.CheckmateError(colour)
            else:
                raise exceptions.StalemateError(colour, 'no moves')
        return check

    def is_check_after_move(self, piece, x, y):
        pieces.Piece.validate_coord(x)
        pieces.Piece.validate_coord(y)

        # Move piece on board, but so that it isn't visible to player
        captured_piece = self.piece_grid[x][y]
        if captured_piece and not isinstance(captured_piece, pieces.EnPassantPawn):
            self.pieces[captured_piece.colour][captured_piece.id] = None
        self.piece_grid[piece.x][piece.y] = None
        self.piece_grid[x][y] = piece
        old_coords = piece.coords
        piece.x, piece.y = x, y

        # Would the move result in a check?
        check = self.is_check(piece.colour)

        # Move everything back
        piece.x, piece.y = old_coords
        self.piece_grid[piece.x][piece.y] = piece
        if captured_piece:
            if not isinstance(captured_piece, pieces.EnPassantPawn):
                self.pieces[captured_piece.colour][captured_piece.id] = captured_piece
            self.piece_grid[x][y] = captured_piece
        else:
            self.piece_grid[x][y] = None
        return check

    def draw_board(self, surface):
        surface.blit(self.tiles, (self.x_offset, self.y_offset))
        surface.blit(self.labels_white, (self.x_offset, self.y_offset))

    def draw_pieces(self, surface):
        self.piece_sprites[0].draw(surface)
        self.piece_sprites[1].draw(surface)
