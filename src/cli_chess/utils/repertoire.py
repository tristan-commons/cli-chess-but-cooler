from __future__ import annotations

import os
from typing import List

import chess

from cli_chess.utils.config import get_config_path


def get_repertoire_dir() -> str:
    return os.path.join(get_config_path(), "repertoires")


def get_repertoire_file_path(color: str) -> str:
    """Returns the full path to the repertoire PGN for the color passed in ('white' or 'black')"""
    filename = "White.pgn" if color.lower() == "white" else "Black.pgn"
    return os.path.join(get_repertoire_dir(), filename)


def repertoire_file_exists(color: str) -> bool:
    """Returns True if the repertoire PGN for the color passed in exists on disk"""
    return os.path.isfile(get_repertoire_file_path(color))


def load_repertoire_lines(file_path: str) -> List[List[chess.Move]]:
    """Loads a repertoire PGN and flattens its variation tree into a list of lines.
       Each line is an ordered list of moves from the starting position to a leaf,
       walked depth-first in the order variations appear in the file (mainline first).
       Raises a ValueError if the file cannot be read as a PGN game.
    """
    import chess.pgn

    with open(file_path, encoding="utf-8") as f:
        game = chess.pgn.read_game(f)

    if game is None:
        raise ValueError(f"Unable to read repertoire: {file_path}")

    return _collect_lines(game, [])


def _collect_lines(node: "chess.pgn.GameNode", path: List[chess.Move]) -> List[List[chess.Move]]:
    """Recursively walks a PGN game node's variations depth-first, returning every
       root-to-leaf line as an ordered list of moves
    """
    if not node.variations:
        return [path]

    lines = []
    for child in node.variations:
        lines.extend(_collect_lines(child, path + [child.move]))
    return lines
