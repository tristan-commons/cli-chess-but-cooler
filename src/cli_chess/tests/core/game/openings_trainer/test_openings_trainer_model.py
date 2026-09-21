from cli_chess.core.game.openings_trainer import OpeningsTrainerModel
from cli_chess.utils import repertoire
from chess import WHITE, BLACK, STARTING_FEN
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
def white_model(repertoire_dir):
    # Two lines sharing the opening move 1.e4, so it's re-quizzed on each line
    write_repertoire(repertoire_dir, "White.pgn", "1. e4 e5 (1... c5 2. Nf3) 2. Nf3 *")
    return OpeningsTrainerModel("white")


@pytest.fixture
def black_model(repertoire_dir):
    write_repertoire(repertoire_dir, "Black.pgn", "1. e4 e5 2. Nf3 Nc6 *")
    return OpeningsTrainerModel("black")


def test_white_model_sets_my_color_and_loads_lines(white_model):
    assert white_model.my_color == WHITE
    assert len(white_model.lines) == 2
    assert white_model.is_my_turn() is True


def test_black_model_autoplays_whites_opening_move_on_init(black_model):
    assert black_model.my_color == BLACK
    assert black_model.current_move_index == 1
    assert black_model.is_my_turn() is True
    assert len(black_model.board_model.board.move_stack) == 1


def test_submit_move_correct_advances_index_and_pushes_move(white_model):
    assert white_model.submit_move("e4") is True
    assert white_model.current_move_index == 1
    assert white_model.board_model.board.move_stack[0].uci() == "e2e4"

    # index advances again once the opponent's reply is auto-played
    white_model.continue_training()
    assert white_model.current_move_index == 2


def test_submit_move_incorrect_returns_false_and_does_not_mutate_board(white_model):
    assert white_model.submit_move("d4") is False
    assert white_model.current_move_index == 0
    assert white_model.board_model.board.move_stack == []


def test_submit_move_accepts_alternate_san_for_same_move(black_model):
    # Black model has already had 1.e4 auto-played; White's Nf3 auto-plays after e5
    black_model.submit_move("e5")
    black_model.continue_training()
    assert black_model.submit_move("Nb8c6") is True


def test_opponent_moves_auto_play_after_correct_trainee_move(white_model):
    white_model.submit_move("e4")
    white_model.continue_training()
    # Black's e5 (or c5) should have auto-played, leaving it White's turn again
    assert white_model.is_my_turn() is True
    assert white_model.current_move_index == 2
    assert len(white_model.board_model.board.move_stack) == 2


def test_line_completion_resets_board_and_advances_to_next_line(white_model):
    white_model.submit_move("e4")
    white_model.continue_training()
    white_model.submit_move("Nf3")
    white_model.continue_training()

    assert white_model.current_line_index == 1
    assert white_model.current_move_index == 0
    assert white_model.board_model.board.fen() == STARTING_FEN
    assert white_model.training_complete is False


def test_full_repertoire_completion_sets_training_complete(white_model):
    white_model.submit_move("e4")
    white_model.continue_training()
    white_model.submit_move("Nf3")
    white_model.continue_training()
    white_model.submit_move("e4")
    white_model.continue_training()
    white_model.submit_move("Nf3")
    white_model.continue_training()

    assert white_model.is_training_complete() is True
    with pytest.raises(Warning):
        white_model.submit_move("e4")


def test_reveal_current_move_does_not_mutate_board(white_model):
    revealed = white_model.reveal_current_move()
    assert revealed.uci() == "e2e4"
    assert white_model.board_model.board.move_stack == []


def test_acknowledge_revealed_move_pushes_move_and_advances(white_model):
    white_model.acknowledge_revealed_move()
    # index advances by 2: the revealed move plus the auto-played opponent reply
    assert white_model.current_move_index == 2
    assert white_model.board_model.board.move_stack[0].uci() == "e2e4"


def test_shared_opening_moves_are_requizzed_across_lines(white_model):
    white_model.submit_move("e4")
    white_model.continue_training()
    white_model.submit_move("Nf3")
    white_model.continue_training()
    assert white_model.current_line_index == 1

    # 1.e4 must be required again for the second line, with no memory of line 1
    assert white_model.submit_move("d4") is False
    assert white_model.submit_move("e4") is True
