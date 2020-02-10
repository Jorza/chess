import pygame
import exceptions
from board import Board


# Global parameters
BLACK = 0, 0, 0
SCREEN = 900, 700
FPS = 60


class Chess:
    def __init__(self):
        self.board = Board()
        self.active_colour = 0  # 0 => white, 1 => black
        self.held_piece = None
        self.check_flag = False

    def pick_up_piece(self, x, y):
        try:
            x, y = self.board.get_board_coords(x, y)
        except ValueError:
            # Clicked outside of board. Do nothing.
            pass
        else:
            piece = self.board.piece_grid[x][y]
            if piece and piece.colour == self.active_colour:  # Player can only move their own pieces
                self.held_piece = piece
                piece.sprite.kill()  # Remove sprite from groups so is not drawn with other pieces
                piece.get_valid_moves()

    def release_piece(self, x, y):
        try:
            x, y = self.board.get_board_coords(x, y)
        except ValueError:
            # Released outside of board. Drop the piece back to current position
            pass
        else:
            if self.held_piece.x != x or self.held_piece.y != y:  # Avoid unnecessary work for trivial case
                if self.board.move(self.held_piece, x, y):
                    self.active_colour = not self.active_colour  # Switch players after a move
                    try:
                        self.check_flag = self.board.is_check_or_checkmate(self.active_colour)
                    except exceptions.GameOverError as e:
                        print(e.message)

        sprite_group = self.board.piece_sprites[self.held_piece.colour]
        self.held_piece.sprite.add(sprite_group)  # Add to group of sprites to draw
        self.held_piece.valid_moves.clear()
        self.held_piece = None  # Drop piece

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            # Picking up a piece on the board
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.pick_up_piece(*event.pos)

            # Placing a held piece on the board
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    if self.held_piece:
                        self.release_piece(*event.pos)

    def draw_game(self, screen):
        self.board.draw_board(screen)
        # Tile overlays
        if self.held_piece:
            for (x, y) in self.held_piece.valid_moves:
                pos = self.board.get_pixel_coords(x, y)
                screen.blit(self.board.moves_overlay, pos)
            screen.blit(self.board.moves_overlay, self.held_piece.sprite.rect)
            screen.blit(self.board.moves_overlay, self.held_piece.sprite.rect)
        if self.check_flag:
            active_king = self.board.pieces[self.active_colour][12]
            screen.blit(self.board.check_overlay, active_king.sprite.rect)
        # Pieces
        self.board.draw_pieces(screen)
        if self.held_piece:
            tile_size = self.board.tile_size
            pos = pygame.mouse.get_pos()
            pos = pos[0] - tile_size // 2, pos[1] - tile_size // 2
            screen.blit(self.held_piece.sprite.image, pos)

    def draw_frame(self, screen):
        # Background
        screen.fill(BLACK)
        self.draw_game(screen)


def play_chess():
    # Initialise, create display, initialise clock
    pygame.init()

    screen = pygame.display.set_mode(SCREEN)
    pygame.display.set_caption("Chess")

    clock = pygame.time.Clock()

    # Program initialisation, first frame logic
    game = Chess()
    game.draw_frame(screen)
    pygame.display.flip()

    # Program loop
    done = False
    while not done:
        # Game logic
        done = game.process_events()

        # Draw game elements
        game.draw_frame(screen)

        # Update display
        pygame.display.flip()  # Update only rects modified in this frame

        # Limit framerate
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    play_chess()
