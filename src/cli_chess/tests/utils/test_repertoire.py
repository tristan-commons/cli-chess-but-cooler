from cli_chess.utils import repertoire
import chess
import pytest
import os


@pytest.fixture
def repertoire_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(repertoire, "get_config_path", lambda: str(tmp_path))
    return tmp_path


def write_pgn(directory, filename: str, content: str) -> str:
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_get_repertoire_dir_mirrors_config_path_convention(repertoire_dir):
    assert repertoire.get_repertoire_dir() == os.path.join(str(repertoire_dir), "repertoires")


def test_get_repertoire_file_path_white_and_black(repertoire_dir):
    assert repertoire.get_repertoire_file_path("white").endswith(os.path.join("repertoires", "White.pgn"))
    assert repertoire.get_repertoire_file_path("black").endswith(os.path.join("repertoires", "Black.pgn"))


def test_repertoire_file_exists_true_and_false(repertoire_dir):
    os.makedirs(repertoire.get_repertoire_dir())
    assert repertoire.repertoire_file_exists("white") is False

    write_pgn(repertoire.get_repertoire_dir(), "White.pgn", "1. e4 *")
    assert repertoire.repertoire_file_exists("white") is True
    assert repertoire.repertoire_file_exists("black") is False


def test_load_repertoire_lines_single_line(tmp_path):
    path = write_pgn(tmp_path, "White.pgn", "1. e4 e5 2. Nf3 Nc6 *")
    lines = repertoire.load_repertoire_lines(path)

    assert len(lines) == 1
    assert [move.uci() for move in lines[0]] == ["e2e4", "e7e5", "g1f3", "b8c6"]


def test_load_repertoire_lines_nested_variations(tmp_path):
    # Mainline: 1.e4 e5 2.Nf3, with two sidelines off Black's first move,
    # one of which itself has a nested sideline off White's second move
    pgn = "1. e4 e5 (1... c5 2. Nf3 (2. c3 d5) 2... d6) (1... c6 2. d4) 2. Nf3 *"
    path = write_pgn(tmp_path, "White.pgn", pgn)
    lines = repertoire.load_repertoire_lines(path)

    san_lines = []
    for line in lines:
        board = chess.Board()
        sans = []
        for move in line:
            sans.append(board.san(move))
            board.push(move)
        san_lines.append(sans)

    assert san_lines == [
        ["e4", "e5", "Nf3"],
        ["e4", "c5", "Nf3", "d6"],
        ["e4", "c5", "c3", "d5"],
        ["e4", "c6", "d4"],
    ]


def test_load_repertoire_lines_raises_on_unreadable_file(tmp_path):
    path = write_pgn(tmp_path, "White.pgn", "")

    with pytest.raises(ValueError):
        repertoire.load_repertoire_lines(path)
