import pygame
import pieces


class Board:
    def __init__(self):
        self.tile_size = 65
        self.x_offset = 200
        self.y_offset = 100

        self.tiles = pygame.image.load("assets/board-tiles.png").convert()
        self.labels_white = pygame.image.load("assets/board-white-labels.png").convert_alpha()
        self.labels_black = pygame.image.load("assets/board-black-labels.png").convert_alpha()

        self.tile_overlay = pygame.Surface((65, 65))
        self.tile_overlay.fill((0, 204, 0))
        self.tile_overlay.set_alpha(0.4)

        self.piece_grid = self.get_grid(8, 8)
        # Bitlists for pieces active in the game (not captured).
        # Each piece has an ID (piece.id) which gives its position in the list. The pawns have IDs 0 - 7 going from file
        # 1 to file 8 (x = 0 to x = 7). The back pieces are numbered similarly, but with 8 - 15.
        # The IDs for corresponding white and black pieces are the same (eg: White King == Black King == 12).
        # pieces[0] => white pieces, pieces[1] => black pieces
        self.pieces = [None] * 16, [None] * 16
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
                pawn = pieces.Pawn(colour, file, pawn_rank, self, file)
                self.pieces[colour][file] = pawn
                self.piece_grid[file][pawn_rank] = pawn
                self.piece_sprites[colour].add(pawn.sprite)
                # Back row pieces
                piece = piece_classes[file](colour, file, back_rank, self, file + 7)
                self.pieces[colour][file + 7] = piece
                self.piece_grid[file][back_rank] = piece
                self.piece_sprites[colour].add(piece.sprite)

    def capture(self, piece):
        pass

    def draw_board(self, surface):
        surface.blit(self.tiles, (self.x_offset, self.y_offset))
        surface.blit(self.labels_white, (self.x_offset, self.y_offset))
        self.piece_sprites[0].draw(surface)
        self.piece_sprites[1].draw(surface)

    def is_attacked(self, x, y, colour):
        for piece in self.pieces[colour]:
            if piece:
                piece.get_valid_moves()
                if (x, y) in piece.valid_moves:
                    return piece
        return False
