from cli_chess.menus import MultiValueMenuModel, MultiValueMenuOption, MenuCategory
from cli_chess.core.game.game_options import GameOption, OfflineGameOptions, OnlinePublicGameOptions, OnlineVsComputerGameOptions, OnlineDirectChallengesGameOptions  # noqa: E501


class VersusMenuModel(MultiValueMenuModel):
    def __init__(self, menu: MenuCategory):
        self.menu = menu
        super().__init__(self.menu)


class OfflineVsComputerMenuModel(VersusMenuModel):
    def __init__(self):
        self.menu = self._create_menu()
        super().__init__(self.menu)

    @staticmethod
    def _create_menu() -> MenuCategory:
        """Create the offline menu options"""
        menu_options = [
            MultiValueMenuOption(GameOption.VARIANT, "Choose the variant to play", [option for option in OfflineGameOptions.variant_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.ENGINE, "Choose the engine to play against", [option for option in OfflineGameOptions.engine_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.COMPUTER_ELO, "Choose the strength of the computer", list(OfflineGameOptions.fairy_stockfish_elo_range)),
            MultiValueMenuOption(GameOption.COLOR, "Choose the side you would like to play as", [option for option in OfflineGameOptions.color_options]),  # noqa: E501
        ]
        return MenuCategory("Play Offline vs Computer", menu_options)

    def update_elo_range_for_engine(self, engine: str):
        """Updates the Computer Elo option's selectable values to match the
           range appropriate for the selected engine (each engine has a
           different set of strength levels it supports)
        """
        elo_range = OfflineGameOptions.maia_elo_range if engine == "Maia" else OfflineGameOptions.fairy_stockfish_elo_range
        for opt in self.menu.category_options:
            if opt.option == GameOption.COMPUTER_ELO:
                opt.values = list(elo_range)
                opt.selected_value = {"index": 0, "name": opt.values[0]}


class OnlineVsComputerMenuModel(VersusMenuModel):
    def __init__(self):
        self.menu = self._create_menu()
        super().__init__(self.menu)

    @staticmethod
    def _create_menu() -> MenuCategory:
        """Create the online menu options"""
        menu_options = [
            MultiValueMenuOption(GameOption.VARIANT, "Choose the variant to play", [option for option in OnlineVsComputerGameOptions.variant_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.TIME_CONTROL, "Choose the time control", [option for option in OnlineVsComputerGameOptions.time_control_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.COMPUTER_SKILL_LEVEL, "Choose the skill level of the computer", [option for option in OnlineVsComputerGameOptions.skill_level_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.COLOR, "Choose the side you would like to play as", [option for option in OnlineVsComputerGameOptions.color_options]),  # noqa: E501
        ]
        return MenuCategory("Play Online vs Computer", menu_options)


class OnlineVsRandomOpponentMenuModel(VersusMenuModel):
    def __init__(self):
        self.menu = self._create_menu()
        super().__init__(self.menu)

    @staticmethod
    def _create_menu() -> MenuCategory:
        """Create the online menu options"""
        menu_options = [
            MultiValueMenuOption(GameOption.VARIANT, "Choose the variant to play", [option for option in OnlinePublicGameOptions.variant_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.TIME_CONTROL, "Choose the time control", [option for option in OnlinePublicGameOptions.time_control_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.RATED, "Choose if you'd like to play a casual or rated game", [option for option in OnlinePublicGameOptions.rated_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.COLOR, "The side you play for an online public game is determined by Lichess", [option for option in OnlinePublicGameOptions.color_options]),  # noqa: E501
        ]
        return MenuCategory("Play Online vs Random Opponent", menu_options)


class OnlineVsPlayerMenuModel(VersusMenuModel):
    def __init__(self):
        self.menu = self._create_menu()
        super().__init__(self.menu)

    @staticmethod
    def _create_menu() -> MenuCategory:
        """Create the challenge a player menu options"""
        menu_options = [
            MultiValueMenuOption(GameOption.VARIANT, "Choose the variant to play", [option for option in OnlineDirectChallengesGameOptions.variant_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.TIME_CONTROL, "Choose the time control", [option for option in OnlineDirectChallengesGameOptions.time_control_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.RATED, "Choose if you'd like to play a casual or rated game", [option for option in OnlineDirectChallengesGameOptions.rated_options_dict]),  # noqa: E501
            MultiValueMenuOption(GameOption.COLOR, "Choose the side you would like to play as", [option for option in OnlineDirectChallengesGameOptions.color_options]),  # noqa: E501
        ]
        return MenuCategory("Challenge a Player", menu_options)
