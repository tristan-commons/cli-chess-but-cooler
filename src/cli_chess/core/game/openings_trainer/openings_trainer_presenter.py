from cli_chess.core.game.openings_trainer import OpeningsTrainerModel, OpeningsTrainerView
from cli_chess.core.game import GamePresenterBase
from cli_chess.utils.ui_common import change_views
from cli_chess.utils import log, AlertType, EventTopics
from prompt_toolkit.application import get_app
from chess import Move
from typing import Optional

# Delay (seconds) between the trainee's move being shown and the opponent's
# auto-played reply appearing, so the two don't render as a single instant jump
OPPONENT_REPLY_DELAY_SECONDS = 0.8


def start_openings_trainer(repertoire_color: str) -> None:
    """Start training the repertoire for the color passed in ('white' or 'black')"""
    presenter = OpeningsTrainerPresenter(OpeningsTrainerModel(repertoire_color))
    change_views(presenter.view, presenter.view.input_field_container)


class OpeningsTrainerPresenter(GamePresenterBase):
    def __init__(self, model: OpeningsTrainerModel):
        self.model = model
        self._revealed_move: Optional[Move] = None
        super().__init__(model)

    def _get_view(self) -> OpeningsTrainerView:
        """Sets and returns the view to use"""
        return OpeningsTrainerView(self)

    def update(self, *args, **kwargs) -> None:
        """Update method called on game model updates. Overrides base."""
        super().update(*args, **kwargs)
        if EventTopics.GAME_END in args and self.model.is_training_complete():
            self.view.alert.show_alert("Repertoire training complete", AlertType.SUCCESS)

    def user_input_received(self, inpt: str) -> None:
        """Respond to the users move input"""
        if self.model.is_training_complete():
            return

        try:
            move = inpt.strip()
            if not move:
                return

            if not self.model.is_my_turn():
                raise Warning("Not your turn")

            if self.model.submit_move(move):
                self.view.alert.clear_alert()
                self._schedule_continue_training()
            else:
                self.view.alert.show_alert("Incorrect move", AlertType.ERROR)
        except Exception as e:
            log.error(e)
            self.view.alert.show_alert(str(e))

    def _schedule_continue_training(self) -> None:
        """Auto-plays the opponent's repertoire reply after OPPONENT_REPLY_DELAY_SECONDS,
           so it doesn't appear on screen at the same instant as the trainee's own move
        """
        loop = get_app().loop
        if loop:
            loop.call_later(OPPONENT_REPLY_DELAY_SECONDS, self._continue_training)
        else:
            self._continue_training()

    def _continue_training(self) -> None:
        """Advances training past the trainee's move. A completion alert may have
           already been shown by update() as a side effect - don't clobber it
        """
        self.model.continue_training()
        if not self.model.is_training_complete():
            self.view.alert.clear_alert()

    def reveal_move(self) -> None:
        """Reveals the move expected at the current position, without making it"""
        self._revealed_move = self.model.reveal_current_move()
        self.view.alert.clear_alert()

    def is_move_revealed(self) -> bool:
        """Returns True if a move is currently revealed and awaiting acknowledgement"""
        return self._revealed_move is not None

    def get_revealed_move_san(self) -> str:
        """Returns the SAN of the currently revealed move, or an empty string if none is revealed"""
        if self._revealed_move is None:
            return ""
        return self.model.board_model.board.san(self._revealed_move)

    def acknowledge_revealed_move(self) -> None:
        """Called once the user has acknowledged the revealed move. Hides the
           reveal and makes the move on the board, continuing training
        """
        if self._revealed_move is None:
            return

        self._revealed_move = None
        self.model.acknowledge_revealed_move()

    def is_training_complete(self) -> bool:
        """Returns True if every line in the repertoire has been completed"""
        return self.model.is_training_complete()
