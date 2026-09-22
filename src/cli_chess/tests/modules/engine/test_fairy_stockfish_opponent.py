from cli_chess.modules.engine import FairyStockfishOpponent
from cli_chess.core.game.game_options import GameOption


def test_get_configuration_uses_selected_elo():
    opponent = FairyStockfishOpponent()
    config = opponent.get_configuration({GameOption.COMPUTER_ELO: 1800})
    assert config == {'UCI_LimitStrength': True, 'UCI_Elo': 1800}


def test_get_configuration_defaults_when_elo_missing():
    opponent = FairyStockfishOpponent()
    config = opponent.get_configuration({})
    assert config == {'UCI_LimitStrength': True, 'UCI_Elo': 1350}


def test_get_search_limit_is_flat_two_seconds():
    opponent = FairyStockfishOpponent()
    limit = opponent.get_search_limit({})
    assert limit.time == 2
    assert limit.nodes is None


def test_get_display_name():
    opponent = FairyStockfishOpponent()
    assert opponent.get_display_name({}) == "Fairy-Stockfish"


def test_get_binary_path_ends_with_fairy_stockfish_binary():
    opponent = FairyStockfishOpponent()
    assert "fairy-stockfish" in opponent.get_binary_path()
