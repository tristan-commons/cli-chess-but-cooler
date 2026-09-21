from cli_chess.core.game.openings_trainer import OpeningsTrainerModel, OpeningsTrainerView
from cli_chess.core.game import GamePresenterBase
from cli_chess.utils.ui_common import change_views
from cli_chess.utils import log, AlertType, EventTopics
from chess import Move
from typing import Optional


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
                # A completion alert may have already been shown by update() as a
                # side effect of submit_move() finishing the repertoire - don't clobber it
                if not self.model.is_training_complete():
                    self.view.alert.clear_alert()
            else:
                self.view.alert.show_alert("Incorrect move", AlertType.ERROR)
        except Exception as e:
            log.error(e)
            self.view.alert.show_alert(str(e))

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
