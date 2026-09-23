from cli_chess.core.game.openings_trainer import OpeningsTrainerModel, OpeningsTrainerPresenter
from cli_chess.utils import repertoire
from unittest.mock import patch
import pytest
import os


@pytest.fixture
def repertoire_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(repertoire, "get_config_path", lambda: str(tmp_path))
    os.makedirs(repertoire.get_repertoire_dir())
    return repertoire.get_repertoire_dir()


def write_repertoire(directory, filename: str, content: str) -> None:
    with open(os.path.join(directory, filename), "w", encoding="utf-8") as f:
        f.write(content)


@pytest.fixture
def presenter(repertoire_dir):
    write_repertoire(repertoire_dir, "White.pgn", "1. e4 e5 2. Nf3 Nc6 *")
    return OpeningsTrainerPresenter(OpeningsTrainerModel("white"))


def fragment_keys(fragments):
    return [text for style, text, *_ in fragments if style == "class:function-bar.key"]


def test_function_bar_never_shows_f3(presenter):
    with patch("cli_chess.utils.ui_common.repaint_ui"):
        fragments = presenter.view._create_function_bar().children[0].content.text()
    assert "F3" not in fragment_keys(fragments)


def test_function_bar_shows_all_active_keys_during_training(presenter):
    with patch("cli_chess.utils.ui_common.repaint_ui"):
        fragments = presenter.view._create_function_bar().children[0].content.text()
    assert fragment_keys(fragments) == ["F1", "F2", "F4", "F5"]


def test_function_bar_hides_show_move_and_notation_when_training_complete(presenter):
    presenter.user_input_received("e4")
    presenter.user_input_received("Nf3")
    assert presenter.is_training_complete() is True

    with patch("cli_chess.utils.ui_common.repaint_ui"):
        fragments = presenter.view._create_function_bar().children[0].content.text()
    assert fragment_keys(fragments) == ["F1", "F4"]


def test_show_move_container_visible_only_when_move_revealed(presenter):
    assert presenter.view.show_move_container.filter() is False

    with patch("cli_chess.utils.ui_common.repaint_ui"):
        presenter.reveal_move()
    assert presenter.view.show_move_container.filter() is True

    presenter.acknowledge_revealed_move()
    assert presenter.view.show_move_container.filter() is False
