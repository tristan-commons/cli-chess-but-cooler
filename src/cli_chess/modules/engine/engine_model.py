from cli_chess.modules.board import BoardModel
from cli_chess.modules.engine.engine_opponent import EngineOpponent
from cli_chess.modules.engine.fairy_stockfish_opponent import FairyStockfishOpponent
from cli_chess.modules.engine.maia_opponent import MaiaOpponent
from cli_chess.core.game.game_options import GameOption
from cli_chess.utils import log
import chess.engine
from typing import Optional


class EngineModel:
    def __init__(self, board_model: BoardModel, game_parameters: dict):
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.board_model = board_model
        self.game_parameters = game_parameters
        self.opponent: EngineOpponent = self._select_opponent()

    def _select_opponent(self) -> EngineOpponent:
        """Selects the engine opponent to use based on the game parameters"""
        engine = self.game_parameters.get(GameOption.ENGINE)
        if engine == "maia":
            return MaiaOpponent()
        return FairyStockfishOpponent()

    def start_engine(self):
        """Starts and configures the selected engine opponent"""
        try:
            # Use SimpleEngine to allow engine assignment in initializer. Additionally,
            # by having this as a blocking call it stops multiple engines from being
            # able to be started if the start game button is spammed
            self.engine = chess.engine.SimpleEngine.popen_uci(self.opponent.get_binary_path())
            self.engine.configure(self.opponent.get_configuration(self.game_parameters))
        except Exception as e:
            msg = f"Error starting engine: {e}"
            log.error(msg)
            raise Warning(msg)

    def get_best_move(self) -> chess.engine.PlayResult:
        """Query the engine to get the best move"""
        # Keep track of the last move that was made. This allows checking
        # for if a takeback happened while the engine has been thinking
        try:
            last_move = (self.board_model.get_move_stack() or [None])[-1]
            result = self.engine.play(self.board_model.board,
                                      self.opponent.get_search_limit(self.game_parameters))

            # Check if the move stack has been altered, if so void this move
            if last_move != (self.board_model.get_move_stack() or [None])[-1]:
                result.move = None

            # Check to make sure the game is still in progress (opponent hasn't resigned)
            if self.board_model.get_game_over_result() is not None:
                result.move = None
        except Exception as e:
            log.error(f"{e}")
            if not self.engine:
                raise Warning("Engine is not running")
            raise

        log.debug(f"Returning {result}")
        return result

    def get_display_name(self) -> str:
        """Returns the display name of the selected engine opponent"""
        return self.opponent.get_display_name(self.game_parameters)

    def quit_engine(self) -> None:
        """Notify the engine to quit"""
        try:
            if self.engine:
                log.debug("Quitting engine")
                self.engine.quit()
        except Exception as e:
            log.error(f"Error quitting engine: {e}")
