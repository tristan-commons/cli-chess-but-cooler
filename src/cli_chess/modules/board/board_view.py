from __future__ import annotations
from cli_chess.utils.ui_common import repaint_ui
from prompt_toolkit.layout import Window, FormattedTextControl, D
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import Box
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cli_chess.modules.board import BoardPresenter


class BoardView:
    # A terminal character cell is roughly twice as tall as it is wide, so a
    # SQUARE_WIDTH:SQUARE_HEIGHT ratio of 6:3 (2:1) renders close to visually
    # square. SQUARE_WIDTH is even so str.center() pads one extra column on
    # the right, offsetting piece glyphs whose ink sits left of their advance
    # width's midpoint in some fonts.
    SQUARE_WIDTH = 6
    SQUARE_HEIGHT = 3

    def __init__(self, presenter: BoardPresenter, initial_board_output: list):
        self.presenter = presenter
        self.board_output = FormattedTextControl(HTML(self._build_output(initial_board_output)))
        self._container = self._create_container()

    def _create_container(self):
        """Create the Board container"""
        width = 2 + 8 * self.SQUARE_WIDTH
        height = 1 + 8 * self.SQUARE_HEIGHT
        return Box(Window(
            self.board_output,
            always_hide_cursor=True,
            width=D(max=width, preferred=width),
            height=D(max=height, preferred=height)
        ), padding=1)

    def _build_output(self, board_output_list: list) -> str:
        """Returns a string containing the board output to be used for
           display. The string returned will contain HTML elements.

           Each square renders as SQUARE_HEIGHT lines, SQUARE_WIDTH columns
           wide, with the piece centered on the middle line.
        """
        board_output_str = ""
        blank_line = ""
        piece_line = ""
        gutter_label = ""

        for square in board_output_list:
            square_style = f"{square['square_display_color']}.{square['piece_display_color']}"
            piece_str = square['piece_str'].center(self.SQUARE_WIDTH)
            blank_str = " " * self.SQUARE_WIDTH

            if not piece_line:
                gutter_label = square['rank_label'] or " "

            piece_line += f"<{square_style}>{piece_str}</{square_style}>"
            blank_line += f"<{square['square_display_color']}>{blank_str}</{square['square_display_color']}>"

            if square['is_end_of_rank']:
                board_output_str += (
                    f"<rank-label>  </rank-label>{blank_line}\n"
                    f"<rank-label>{gutter_label} </rank-label>{piece_line}\n"
                    f"<rank-label>  </rank-label>{blank_line}\n"
                )
                blank_line = ""
                piece_line = ""

        file_labels = self._center_file_labels(self.presenter.get_file_labels())
        board_output_str += f"<rank-label> </rank-label><file-label>{file_labels}</file-label>"

        return board_output_str

    @classmethod
    def _center_file_labels(cls, file_labels: str) -> str:
        """Returns the file labels with each letter centered in a
           SQUARE_WIDTH-char cell, matching the piece cells above"""
        return " " + "".join(letter.center(cls.SQUARE_WIDTH) for letter in file_labels.split())

    def update(self, board_output_list: list):
        """Updates the board output with the passed in text"""
        self.board_output.text = HTML(self._build_output(board_output_list))
        repaint_ui()

    def __pt_container__(self) -> Box:
        """Returns this container"""
        return self._container
