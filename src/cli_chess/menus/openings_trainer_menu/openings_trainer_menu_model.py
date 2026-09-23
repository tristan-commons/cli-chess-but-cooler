from cli_chess.menus import MultiValueMenuModel, MultiValueMenuOption, MenuCategory
from enum import Enum


class RepertoireColor(Enum):
    REPERTOIRE = "Repertoire"


class OpeningsTrainerMenuModel(MultiValueMenuModel):
    def __init__(self):
        self.menu = self._create_menu()
        super().__init__(self.menu)

    @staticmethod
    def _create_menu() -> MenuCategory:
        """Create the openings trainer menu options"""
        menu_options = [
            MultiValueMenuOption(RepertoireColor.REPERTOIRE, "Choose the repertoire to train", ["White", "Black"]),
        ]
        return MenuCategory("Train Openings", menu_options)
