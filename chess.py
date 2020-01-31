import pygame
import board


# Global parameters
BLACK = 0, 0, 0
SCREEN = 900, 700
FPS = 60


class Chess:
    def __init__(self):
        self.board = board.Board()
        self.active_colour = 0  # 0 => white, 1 => black
        self.held_piece = None

    def get_board_coords(self, x, y):
        board = self.board
        x, y = (x - board.x_offset) // board.tile_size, (y - board.y_offset) // board.tile_size
        if x < 0 or x > 7 or y < 0 or y > 7:
            raise ValueError("Coordinates are not on the board")
        return x, y

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            # Picking up a piece on the board
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    try:
                        x, y = self.get_board_coords(*event.pos)
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
                        x, y = self.get_board_coords(*event.pos)
                        if (x, y) in self.held_piece.valid_moves:
                            captured_piece = self.board.piece_grid[x][y]
                            if captured_piece:
                                board.capture(captured_piece)
                            piece = self.held_piece
                            piece.move(x, y)
                            piece.sprite.add(self.board.piece_sprites[piece.colour])  # Add to group of sprites to draw
                            self.held_piece = None  # Drop piece
                            self.active_colour = not self.active_colour  # Switch players after a move
                    except ValueError:
                        # Released outside of board. Drop the piece back to current position
                        piece = self.held_piece
                        piece.sprite.rect.x, piece.sprite.rect.y = piece.screen_pixel_coords  # Reset sprite position
                        piece.sprite.add(self.board.piece_sprites[piece.colour])  # Add to group of sprites to draw

    def draw_frame(self, screen):
        screen.fill(BLACK)
        self.board.draw_board(screen)


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
