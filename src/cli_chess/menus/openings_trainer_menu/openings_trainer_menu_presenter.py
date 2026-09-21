from __future__ import annotations
from cli_chess.menus.openings_trainer_menu import OpeningsTrainerMenuView
from cli_chess.menus import MultiValueMenuPresenter
from cli_chess.core.game import start_openings_trainer
from cli_chess.utils.repertoire import repertoire_file_exists
from cli_chess.utils import log
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cli_chess.menus.openings_trainer_menu import OpeningsTrainerMenuModel


class OpeningsTrainerMenuPresenter(MultiValueMenuPresenter):
    """Defines the presenter for the openings trainer repertoire picker menu"""
    def __init__(self, model: OpeningsTrainerMenuModel):
        self.model = model
        self.view = OpeningsTrainerMenuView(self)
        super().__init__(self.model, self.view)

    def get_selected_color(self) -> str:
        """Returns the currently selected repertoire color ('white' or 'black')"""
        return self.model.get_menu_options()[0].selected_value['name'].lower()

    def is_repertoire_missing(self) -> bool:
        """Returns True if the PGN for the currently selected repertoire color doesn't exist"""
        return not repertoire_file_exists(self.get_selected_color())

    def handle_start_training(self) -> None:
        """Starts training the currently selected repertoire"""
        if self.is_repertoire_missing():
            return

        try:
            start_openings_trainer(self.get_selected_color())
        except Exception as e:
            log.error(e)
            raise
