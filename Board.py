import pygame
import Pieces


class Board:
    def __init__(self):
        self.tile_size = 65
        self.x_offset = 200
        self.y_offset = 100

        self.tiles = pygame.image.load("assets/board-tiles.png").convert()
        self.labels_white = pygame.image.load("assets/board-white-labels.png").convert_alpha()
        self.labels_black = pygame.image.load("assets/board-black-labels.png").convert_alpha()

        self.piece_grid = self.get_grid(8, 8)
        self.pieces = [], []  # pieces[0] => white pieces, pieces[1] => black pieces
        self.piece_sprites = pygame.sprite.Group(), pygame.sprite.Group()

        self.set_pieces()

    @staticmethod
    def get_grid(m, n):
        grid = []
        for i in range(m):
            grid.append([None] * n)
        return grid

    def set_pieces(self):
        # Pawns
        for i in range(8):
            self.pieces[0].append(Pieces.Pawn(0, i, 6, self))
            self.pieces[1].append(Pieces.Pawn(1, i, 1, self))
        # Rooks
        for i in [0, 7]:
            self.pieces[0].append(Pieces.Rook(0, i, 7, self))
            self.pieces[1].append(Pieces.Rook(1, i, 0, self))
        # Knights
        for i in [1, 6]:
            self.pieces[0].append(Pieces.Knight(0, i, 7, self))
            self.pieces[1].append(Pieces.Knight(1, i, 0, self))
        # Bishops
        for i in [2, 5]:
            self.pieces[0].append(Pieces.Bishop(0, i, 7, self))
            self.pieces[1].append(Pieces.Bishop(1, i, 0, self))
        # Queens
        self.pieces[0].append(Pieces.Queen(0, 3, 7, self))
        self.pieces[0].append(Pieces.Queen(1, 3, 0, self))
        # Kings
        self.pieces[0].append(Pieces.King(0, 4, 7, self))
        self.pieces[0].append(Pieces.King(1, 4, 0, self))

        # Sprites
        for colour in [0, 1]:
            for piece in self.pieces[colour]:
                self.piece_sprites[colour].add(piece.sprite)

    def draw_board(self, surface):
        surface.blit(self.tiles, (self.x_offset, self.y_offset))
        surface.blit(self.labels_white, (self.x_offset, self.y_offset))
        self.piece_sprites[0].draw(surface)
        self.piece_sprites[1].draw(surface)

    def is_attacked(self, x, y, colour):
        for piece in self.pieces[colour]:
            piece.get_valid_moves()
            if (x, y) in piece.valid_moves:
                return piece
        return False


def play_chess():
    # Parameters
    BLACK = 0, 0, 0
    SCREEN = 900, 700
    FPS = 60

    # Initialise, create display, initialise clock
    pygame.init()

    screen = pygame.display.set_mode(SCREEN)
    pygame.display.set_caption("Chess")

    clock = pygame.time.Clock()

    # Program initialisation, first frame logic
    board = Board()
    screen.fill(BLACK)
    board.draw_board(screen)
    pygame.display.flip()

    # Program loop
    done = False
    while not done:
        # Game logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Draw game elements
        board.draw_board(screen)

        # Update display
        pygame.display.flip()  # Update only rects modified in this frame

        # Limit framerate
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    play_chess()
