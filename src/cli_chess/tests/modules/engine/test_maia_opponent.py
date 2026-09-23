from cli_chess.modules.engine import MaiaOpponent
from cli_chess.core.game.game_options import GameOption


def test_get_configuration_uses_selected_rating():
    opponent = MaiaOpponent()
    config = opponent.get_configuration({GameOption.COMPUTER_ELO: 1500})
    assert config['WeightsFile'].endswith("maia-1500.pb.gz")


def test_get_configuration_defaults_when_rating_missing():
    opponent = MaiaOpponent()
    config = opponent.get_configuration({})
    assert config['WeightsFile'].endswith("maia-1500.pb.gz")


def test_get_search_limit_is_a_single_node_with_no_time_bound():
    """Maia must be run with search disabled (nodes=1). This must never
       regress to also carrying a time bound alongside the node limit.
    """
    opponent = MaiaOpponent()
    limit = opponent.get_search_limit({GameOption.COMPUTER_ELO: 1900})
    assert limit.nodes == 1
    assert limit.time is None


def test_get_display_name_includes_rating():
    opponent = MaiaOpponent()
    assert opponent.get_display_name({GameOption.COMPUTER_ELO: 1700}) == "Maia 1700"


def test_get_binary_path_points_at_lc0():
    opponent = MaiaOpponent()
    assert "lc0" in opponent.get_binary_path()
