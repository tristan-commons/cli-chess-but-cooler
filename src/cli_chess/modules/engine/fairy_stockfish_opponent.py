from cli_chess.modules.engine.engine_opponent import EngineOpponent
from cli_chess.core.game.game_options import GameOption
from cli_chess.utils import is_linux_os, is_windows_os, is_mac_os
import chess.engine
from os import path
import platform


class FairyStockfishOpponent(EngineOpponent):
    """Defines the Fairy-Stockfish engine opponent"""
    def get_binary_path(self) -> str:
        """Returns the path to the Fairy-Stockfish binary to use for this platform"""
        binary_name = "fairy-stockfish_x86-64_" + ("linux" if is_linux_os() else ("windows" if is_windows_os() else "macos"))
        if is_mac_os() and platform.machine() == "arm64":
            binary_name = "fairy-stockfish_arm64_macos"
        return path.dirname(path.realpath(__file__)) + "/binaries/" + binary_name

    def get_configuration(self, game_parameters: dict) -> dict:
        """Returns the UCI options to configure Fairy-Stockfish with"""
        uci_elo = game_parameters.get(GameOption.COMPUTER_ELO)
        return {
            'UCI_LimitStrength': True,
            'UCI_Elo': uci_elo if uci_elo else 1350
        }

    def get_search_limit(self, game_parameters: dict) -> chess.engine.Limit:
        """Fairy-Stockfish is given a flat 2 second move time"""
        return chess.engine.Limit(2)

    def get_display_name(self, game_parameters: dict) -> str:
        """Returns the display name for Fairy-Stockfish"""
        return "Fairy-Stockfish"
