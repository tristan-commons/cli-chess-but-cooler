from cli_chess.core.game.openings_trainer import OpeningsTrainerModel, OpeningsTrainerPresenter
from cli_chess.utils import repertoire
from cli_chess.utils.common import AlertType
from unittest.mock import Mock
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


def test_correct_move_clears_alert(presenter):
    presenter.view.alert.show_alert("Incorrect move", AlertType.ERROR)
    presenter.user_input_received("e4")

    assert presenter.view.alert._alert_label.text == ""


def test_incorrect_move_shows_incorrect_alert_and_does_not_mutate_board(presenter):
    presenter.user_input_received("d4")

    assert presenter.view.alert._alert_label.text == "Incorrect move"
    assert presenter.model.board_model.board.move_stack == []


def test_malformed_input_shows_translated_value_error_alert(presenter):
    presenter.user_input_received("not a move")

    assert "Invalid move" in presenter.view.alert._alert_label.text
    assert presenter.model.board_model.board.move_stack == []


def test_input_ignored_once_training_complete(presenter):
    presenter.user_input_received("e4")
    presenter.user_input_received("Nf3")

    assert presenter.is_training_complete() is True
    move_stack_before = list(presenter.model.board_model.board.move_stack)

    presenter.user_input_received("e4")
    assert presenter.model.board_model.board.move_stack == move_stack_before


def test_reveal_move_sets_revealed_state_without_mutating_board(presenter):
    presenter.reveal_move()

    assert presenter.is_move_revealed() is True
    assert presenter.get_revealed_move_san() == "e4"
    assert presenter.model.board_model.board.move_stack == []


def test_reveal_move_clears_a_stale_incorrect_move_alert(presenter):
    presenter.user_input_received("d4")
    assert presenter.view.alert._alert_label.text == "Incorrect move"

    presenter.reveal_move()
    assert presenter.view.alert._alert_label.text == ""


def test_acknowledge_revealed_move_hides_reveal_and_plays_move(presenter):
    presenter.reveal_move()
    presenter.acknowledge_revealed_move()

    assert presenter.is_move_revealed() is False
    assert presenter.model.board_model.board.move_stack[0].uci() == "e2e4"


def test_update_shows_completion_alert_on_training_complete(presenter):
    presenter.user_input_received("e4")
    presenter.user_input_received("Nf3")

    assert presenter.view.alert._alert_label.text == "Repertoire training complete"


def test_is_training_complete_reflects_model_state(presenter):
    assert presenter.is_training_complete() is False
    presenter.user_input_received("e4")
    presenter.user_input_received("Nf3")
    assert presenter.is_training_complete() is True


def test_exit_does_not_save_pgn(presenter, monkeypatch):
    from cli_chess.core.game import game_presenter_base, game_view_base
    save_spy = Mock()
    monkeypatch.setattr(game_presenter_base, "save_game_pgn", save_spy)
    monkeypatch.setattr(game_view_base, "go_back_to_main_menu", Mock())

    presenter.user_input_received("e4")
    presenter.exit()

    assert save_spy.call_count == 0
