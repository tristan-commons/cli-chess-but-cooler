from cli_chess.core.game import GameModelBase
from cli_chess.utils import EventTopics, log
from cli_chess.utils.repertoire import get_repertoire_file_path, load_repertoire_lines
import chess
from chess import Color, COLOR_NAMES, Move
from typing import List, Optional


class OpeningsTrainerModel(GameModelBase):
    def __init__(self, repertoire_color: str):
        self.my_color: Color = Color(COLOR_NAMES.index(repertoire_color.lower()))
        super().__init__(orientation=self.my_color, variant="standard", fen="", side_confirmed=True)

        self.lines: List[List[Move]] = load_repertoire_lines(get_repertoire_file_path(repertoire_color))
        self.current_line_index = 0
        self.current_move_index = 0
        self.training_complete = False

        self._advance_after_correct_move()

    def is_my_turn(self) -> bool:
        """Return True if it's the trainee's turn"""
        return self.board_model.get_turn() == self.my_color

    def is_training_complete(self) -> bool:
        """Returns True if every line in the repertoire has been completed"""
        return self.training_complete

    def get_expected_move(self) -> Optional[Move]:
        """Returns the next move expected at the current position, or None
           if training has completed
        """
        if self.training_complete:
            return None
        return self.lines[self.current_line_index][self.current_move_index]

    def submit_move(self, move: str) -> bool:
        """Attempts to make the trainee's move. Returns True if the move matches
           the expected move for this position and was made, otherwise returns False
           and leaves the board untouched. Raises an exception if training has already
           completed, it's not the trainee's turn, or the move cannot be parsed.
        """
        if self.training_complete:
            raise Warning("Repertoire training complete")

        if not self.is_my_turn():
            raise Warning("Not your turn")

        move = move.strip()
        try:
            parsed_move = self.board_model.board.parse_san(move)
        except Exception as e:
            log.error(e)
            if isinstance(e, chess.InvalidMoveError):
                raise ValueError(f"Invalid move: {move}")
            elif isinstance(e, chess.IllegalMoveError):
                raise ValueError(f"Illegal move: {move}")
            elif isinstance(e, chess.AmbiguousMoveError):
                raise ValueError(f"Ambiguous move: {move}")
            else:
                raise e

        if parsed_move != self.get_expected_move():
            return False

        self.board_model.make_move(move)
        self.current_move_index += 1
        return True

    def continue_training(self) -> None:
        """Auto-plays the opponent's repertoire reply (and any further advancement)
           following a correct trainee move. Called by the presenter - optionally
           after a delay so the reply isn't shown to the trainee instantly.
        """
        self._advance_after_correct_move()

    def reveal_current_move(self) -> Optional[Move]:
        """Returns the move expected at the current position, without making it"""
        return self.get_expected_move()

    def acknowledge_revealed_move(self) -> None:
        """Makes the previously revealed move on the board and continues training.
           Should only be called after the user has acknowledged the reveal.
        """
        move = self.get_expected_move()
        if move is None:
            return

        self.board_model.make_move(self.board_model.board.san(move))
        self.current_move_index += 1
        self._advance_after_correct_move()

    def _advance_after_correct_move(self) -> None:
        """Steps the training state forward after a move has been made: auto-plays
           consecutive opponent replies from the repertoire, and advances to the next
           line (or completes training) once the current line is exhausted. Stops as
           soon as it's the trainee's turn again with moves remaining in the line.
        """
        current_line = self.lines[self.current_line_index]

        if self.current_move_index >= len(current_line):
            self._advance_to_next_line()
        elif not self.is_my_turn():
            opponent_move = current_line[self.current_move_index]
            self.board_model.make_move(self.board_model.board.san(opponent_move))
            self.current_move_index += 1
            self._advance_after_correct_move()

    def _advance_to_next_line(self) -> None:
        """Resets the board and advances to the next line in the repertoire.
           Marks training as complete once every line has been played
        """
        self.current_line_index += 1
        self.current_move_index = 0

        # notify=True so the board/move-list/material-diff displays refresh to the
        # reset position; this also bubbles up as EventTopics.GAME_START for listeners
        self.board_model.reset(notify=True)

        if self.current_line_index >= len(self.lines):
            self.training_complete = True
            log.info("Openings trainer: repertoire training complete")
            self._notify_game_model_updated(EventTopics.GAME_END)
            return

        self._advance_after_correct_move()
