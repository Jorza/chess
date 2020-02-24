import pygame
import exceptions
from board import Board
import pieces


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
        self.pawn_promotion = None

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

    def turnover_move(self):
        self.active_colour = not self.active_colour  # Switch players
        if self.board.en_passant_pawn:
            self.board.remove_en_passant_pawn()
        try:
            self.check_flag = self.board.is_check_or_checkmate(self.active_colour)
        except exceptions.GameOverError as e:
            print(e.message)

    def release_piece(self, x, y):
        try:
            x, y = self.board.get_board_coords(x, y)
        except ValueError:
            # Released outside of board. Drop the piece back to current position
            pass
        else:
            if self.held_piece.x != x or self.held_piece.y != y:  # Avoid unnecessary work for trivial case
                if (x, y) in self.held_piece.valid_moves:
                    try:
                        self.board.move(self.held_piece, x, y)
                    except exceptions.PawnPromotionError as e:
                        self.pawn_promotion = e
                        self.held_piece = None
                        # Must drop the piece here
                        # Only restore the sprite and clear the valid moves if the promotion is cancelled.
                        return
                    else:
                        self.turnover_move()

        self.board.add_piece_sprite(self.held_piece)  # Add to group of sprites to draw
        self.held_piece.valid_moves.clear()
        self.held_piece = None  # Drop piece

    def select_promotion(self, x, y):
        promotion = self.pawn_promotion
        self.pawn_promotion = None
        try:
            x, y = self.board.get_board_coords(x, y)
            if x != promotion.x or ((y > 3) ^ promotion.pawn.colour):
                raise ValueError
        except ValueError:
            # Clicked outside of promotion selection area. Cancel promotion, restore old pawn.
            self.board.add_piece_sprite(promotion.pawn)  # Add to group of sprites to draw
            promotion.pawn.valid_moves.clear()
            return

        # Selected a piece to promote to.
        piece_index = y if y < 4 else 7 - y
        possible_promotions = pieces.Queen, pieces.Rook, pieces.Bishop, pieces.Knight
        promotion_piece = possible_promotions[piece_index]

        # Promote piece, end move.
        self.board.promote(promotion, promotion_piece)
        self.turnover_move()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    # Pawn promotion
                    if self.pawn_promotion:
                        self.select_promotion(*event.pos)
                    # Picking up a piece on the board
                    else:
                        self.pick_up_piece(*event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    # Placing a held piece on the board
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
        # Pawn promotion overlay
        if self.pawn_promotion:
            if self.pawn_promotion.pawn.colour:
                pos = self.board.get_pixel_coords(self.pawn_promotion.x, 4)
                image = self.board.pawn_promotions_black
            else:
                pos = self.board.get_pixel_coords(self.pawn_promotion.x, 0)
                image = self.board.pawn_promotions_white
            screen.blit(image, pos)

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
