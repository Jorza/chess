import pygame
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

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            # Picking up a piece on the board
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    try:
                        x, y = self.board.get_board_coords(*event.pos)
                        piece = self.board.piece_grid[x][y]
                        if piece and piece.colour == self.active_colour:
                            self.held_piece = piece
                            piece.sprite.kill()  # Remove sprite from groups so is not drawn with other pieces
                            piece.get_valid_moves()
                    except ValueError:
                        # Clicked outside of board. Do nothing.
                        pass
            # Placing a held piece on the board
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT and self.held_piece:
                    try:
                        x, y = self.board.get_board_coords(*event.pos)
                    except ValueError:
                        # Released outside of board. Drop the piece back to current position
                        pass
                    else:
                        if (x, y) in self.held_piece.valid_moves:
                            captured_piece = self.board.piece_grid[x][y]
                            if captured_piece:
                                self.board.capture(captured_piece)
                            self.board.move(self.held_piece, x, y)
                            self.active_colour = not self.active_colour  # Switch players after a move
                    sprite_group = self.board.piece_sprites[self.held_piece.colour]
                    self.held_piece.sprite.add(sprite_group)  # Add to group of sprites to draw
                    self.held_piece = None  # Drop piece

    def draw_frame(self, screen):
        screen.fill(BLACK)
        self.board.draw_board(screen)
        if self.held_piece:
            for (x, y) in self.held_piece.valid_moves:
                pos = self.board.get_pixel_coords(x, y)
                screen.blit(self.board.tile_overlay, pos)
            screen.blit(self.board.tile_overlay, self.held_piece.sprite.rect)
            screen.blit(self.board.tile_overlay, self.held_piece.sprite.rect)

            tile_size = self.board.tile_size
            pos = pygame.mouse.get_pos()
            pos = pos[0] - tile_size // 2, pos[1] - tile_size // 2
            screen.blit(self.held_piece.sprite.image, pos)


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
