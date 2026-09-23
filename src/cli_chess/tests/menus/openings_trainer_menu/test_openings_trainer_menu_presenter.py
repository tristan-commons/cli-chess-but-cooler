from cli_chess.menus.openings_trainer_menu import OpeningsTrainerMenuModel, OpeningsTrainerMenuPresenter
from cli_chess.utils import repertoire
from unittest.mock import Mock
import pytest
import os


@pytest.fixture
def repertoire_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(repertoire, "get_config_path", lambda: str(tmp_path))
    os.makedirs(repertoire.get_repertoire_dir())
    return repertoire.get_repertoire_dir()


@pytest.fixture
def presenter(repertoire_dir):
    return OpeningsTrainerMenuPresenter(OpeningsTrainerMenuModel())


def test_get_selected_color_reflects_selected_value(presenter):
    assert presenter.get_selected_color() == "white"

    presenter.model.get_menu_options()[0].next_value()
    assert presenter.get_selected_color() == "black"


def test_is_repertoire_missing_true_when_file_absent(presenter):
    assert presenter.is_repertoire_missing() is True


def test_is_repertoire_missing_false_when_file_present(presenter, repertoire_dir):
    with open(os.path.join(repertoire_dir, "White.pgn"), "w", encoding="utf-8") as f:
        f.write("1. e4 *")

    assert presenter.is_repertoire_missing() is False


def test_handle_start_training_noop_when_repertoire_missing(presenter, monkeypatch):
    from cli_chess.menus.openings_trainer_menu import openings_trainer_menu_presenter
    spy = Mock()
    monkeypatch.setattr(openings_trainer_menu_presenter, "start_openings_trainer", spy)

    presenter.handle_start_training()

    spy.assert_not_called()


def test_handle_start_training_starts_trainer_when_repertoire_present(presenter, repertoire_dir, monkeypatch):
    with open(os.path.join(repertoire_dir, "White.pgn"), "w", encoding="utf-8") as f:
        f.write("1. e4 *")

    from cli_chess.menus.openings_trainer_menu import openings_trainer_menu_presenter
    spy = Mock()
    monkeypatch.setattr(openings_trainer_menu_presenter, "start_openings_trainer", spy)

    presenter.handle_start_training()

    spy.assert_called_once_with("white")
