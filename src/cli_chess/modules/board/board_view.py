from __future__ import annotations
from cli_chess.utils.ui_common import repaint_ui
from prompt_toolkit.layout import Window, FormattedTextControl, D
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import Box
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cli_chess.modules.board import BoardPresenter


class BoardView:
    def __init__(self, presenter: BoardPresenter, initial_board_output: list):
        self.presenter = presenter
        self.board_output = FormattedTextControl(HTML(self._build_output(initial_board_output)))
        self._container = self._create_container()

    SQUARE_WIDTH = 5
    SQUARE_HEIGHT = 3

    def _create_container(self):
        """Create the Board container"""
        return Box(Window(
            self.board_output,
            always_hide_cursor=True,
            width=D(max=1 + 8 * self.SQUARE_WIDTH, preferred=1 + 8 * self.SQUARE_WIDTH),
            height=D(max=1 + 8 * self.SQUARE_HEIGHT, preferred=1 + 8 * self.SQUARE_HEIGHT)
        ), padding=1)

    def _build_output(self, board_output_list: list) -> str:
        """Returns a string containing the board output to be used for
           display. The string returned will contain HTML elements.

           Each square renders as SQUARE_HEIGHT lines, SQUARE_WIDTH columns wide,
           with the piece centered on the middle line. The width:height ratio per
           square (6:3 = 2) matches a monospace terminal character's approximate
           2:1 height:width aspect, keeping the overall board visually square.
        """
        board_output_str = ""
        blank_line = " "
        piece_line = ""

        for square in board_output_list:
            square_style = f"{square['square_display_color']}.{square['piece_display_color']}"
            piece_str = square['piece_str'].center(self.SQUARE_WIDTH)
            blank_str = " " * self.SQUARE_WIDTH

            piece_line += f"<rank-label>{square['rank_label']}</rank-label>"
            piece_line += f"<{square_style}>{piece_str}</{square_style}>"

            blank_line += f"<{square['square_display_color']}>{blank_str}</{square['square_display_color']}>"

            if square['is_end_of_rank']:
                board_output_str += f"{blank_line}\n{piece_line}\n{blank_line}\n"
                blank_line = " "
                piece_line = ""

        file_labels = " " + self._center_file_labels(self.presenter.get_file_labels())
        board_output_str += f"<file-label>{file_labels}</file-label>"

        return board_output_str

    @classmethod
    def _center_file_labels(cls, file_labels: str) -> str:
        """Returns the file labels with each letter centered in a
           SQUARE_WIDTH-char cell, matching the piece cells above"""
        return "".join(letter.center(cls.SQUARE_WIDTH) for letter in file_labels.split())

    def update(self, board_output_list: list):
        """Updates the board output with the passed in text"""
        self.board_output.text = HTML(self._build_output(board_output_list))
        repaint_ui()

    def __pt_container__(self) -> Box:
        """Returns this container"""
        return self._container
