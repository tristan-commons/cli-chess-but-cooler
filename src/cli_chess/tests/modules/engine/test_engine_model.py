from cli_chess.modules.engine import EngineModel, FairyStockfishOpponent, MaiaOpponent
from cli_chess.core.game.game_options import GameOption
from unittest.mock import Mock


def test_select_opponent_returns_maia_when_engine_is_maia():
    model = EngineModel(Mock(), {GameOption.ENGINE: "maia"})
    assert isinstance(model.opponent, MaiaOpponent)


def test_select_opponent_returns_fairy_stockfish_when_engine_is_fairy_stockfish():
    model = EngineModel(Mock(), {GameOption.ENGINE: "fairy-stockfish"})
    assert isinstance(model.opponent, FairyStockfishOpponent)


def test_select_opponent_defaults_to_fairy_stockfish_when_engine_missing():
    model = EngineModel(Mock(), {})
    assert isinstance(model.opponent, FairyStockfishOpponent)


def test_get_display_name_delegates_to_opponent():
    model = EngineModel(Mock(), {GameOption.ENGINE: "maia", GameOption.COMPUTER_ELO: 1300})
    assert model.get_display_name() == "Maia 1300"
