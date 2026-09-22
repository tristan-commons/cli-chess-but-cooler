from cli_chess.modules.engine.engine_opponent import EngineOpponent
from cli_chess.core.game.game_options import GameOption
from cli_chess.utils import is_linux_os, is_windows_os, is_mac_os
import chess.engine
from os import path
import platform

MAIA_RATING_LEVELS = list(range(1100, 2000, 100))
MAIA_DEFAULT_RATING = 1500


class MaiaOpponent(EngineOpponent):
    """Defines the Maia engine opponent. Maia is a set of human-like neural
       network weights run through the lc0 (Leela Chess Zero) engine. Maia
       is a pure policy network - it must be run with search disabled
       (a node limit of 1) to produce its intended human-like moves.
    """
    def get_binary_path(self) -> str:
        """Returns the path to the lc0 binary to use for this platform"""
        binary_name = "lc0_x86-64_" + ("linux" if is_linux_os() else ("windows.exe" if is_windows_os() else "macos"))
        if is_mac_os() and platform.machine() == "arm64":
            binary_name = "lc0_arm64_macos"
        return path.dirname(path.realpath(__file__)) + "/binaries/lc0/" + binary_name

    def get_configuration(self, game_parameters: dict) -> dict:
        """Returns the UCI options to configure lc0 with the correct Maia weights"""
        rating = game_parameters.get(GameOption.COMPUTER_ELO) or MAIA_DEFAULT_RATING
        weights_dir = path.dirname(path.realpath(__file__)) + "/binaries/maia_weights"
        return {
            'WeightsFile': f"{weights_dir}/maia-{rating}.pb.gz"
        }

    def get_search_limit(self, game_parameters: dict) -> chess.engine.Limit:
        """Maia must be run with search disabled - a node limit of 1 - to
           produce its intended human-like moves. This must never be
           configurable or overridden.
        """
        return chess.engine.Limit(nodes=1)

    def get_display_name(self, game_parameters: dict) -> str:
        """Returns the display name for Maia, including its rating level"""
        rating = game_parameters.get(GameOption.COMPUTER_ELO) or MAIA_DEFAULT_RATING
        return f"Maia {rating}"
