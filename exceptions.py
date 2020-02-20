class PawnPromotionError(Exception):
    """
    Raised when a pawn reaches the back rank.

    Interrupts the current move so that the user can select the promotion they want.
    """
    def __init__(self, pawn, x, y):
        self.pawn = pawn
        # Store the board coordinates where the pawn is to be promoted.
        # These are not the pawn's current coordinates.
        self.x = x
        self.y = y

    @property
    def properties(self):
        return self.pawn, self.x, self.y


class GameOverError(Exception):
    """
    Base class for all user-defined exceptions signalling a completed game.
    """
    def __init__(self, colour):
        self.colour = colour
        self.message = None  # Override this in subclasses

    @staticmethod
    def get_colour_string(colour):
        return 'Black' if colour else 'White'


class CheckmateError(GameOverError):
    """
    Raised when the game ends by Checkmate.

    Attributes:
        colour -- Colour of the player who is in checkmate (the loser).
    """
    def __init__(self, colour):
        super().__init__(colour)
        self.message = 'Checkmate! ' + self.get_colour_string(not self.colour) + ' wins.'


class StalemateError(GameOverError):
    """
    Raised when the game ends by Stalemate by any cause.

    Attributes:
        colour -- Colour of the player whose turn it is.
        cause -- One of the 3 causes of stalemate:
                    0. No valid moves for current player
                    1. 50 moves without a capture or a pawn move
                    2. Repeated the same board position 3 times
    """
    causes = ['No moves', 'No progress', 'Repeated moves']
    messages = ['No valid moves left.', '50 moves without a capture or a pawn move.', 'Repeated the same board position 3 times.']

    def __init__(self, colour, cause):
        super().__init__(colour)
        if isinstance(cause, str):
            cause = cause.lower()
            for i in range(len(self.causes)):
                if cause == self.causes[i].lower():
                    cause = i
        if isinstance(cause, int) and 0 <= cause <= 2:
            self.cause = self.causes[cause]
            self.message = 'Stalemate! ' + self.messages[cause]


class TimeControlError(GameOverError):
    """
        Raised when the game ends by a player running out of time.

        Attributes:
            colour -- Colour of the player whose turn it is (the loser).
        """

    def __init__(self, colour):
        super().__init__(colour)
        self.message = 'Timeout! ' + self.get_colour_string(not self.colour) + ' wins.'
