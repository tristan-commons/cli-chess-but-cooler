from __future__ import annotations
from cli_chess.menus import MultiValueMenuView
from cli_chess.utils.ui_common import handle_mouse_click, handle_bound_key_pressed
from cli_chess.utils.repertoire import get_repertoire_dir
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import Container, ConditionalContainer, HSplit
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.widgets import TextArea
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cli_chess.menus.openings_trainer_menu import OpeningsTrainerMenuPresenter


class OpeningsTrainerMenuView(MultiValueMenuView):
    def __init__(self, presenter: OpeningsTrainerMenuPresenter):
        self.presenter = presenter
        super().__init__(self.presenter, container_width=24, column_width=10)

    def _create_container(self) -> Container:
        """Wraps the repertoire picker with a placeholder message shown when
           the selected repertoire's PGN file doesn't exist
        """
        self._menu_container = super()._create_container()
        return HSplit([
            ConditionalContainer(
                self._menu_container,
                filter=~Condition(self.presenter.is_repertoire_missing)
            ),
            ConditionalContainer(
                TextArea(
                    "Repertoire file not found.\n"
                    "Add a PGN file at:\n"
                    f"{get_repertoire_dir()}/White.pgn (or Black.pgn)",
                    wrap_lines=True, read_only=True, focusable=False
                ),
                filter=Condition(self.presenter.is_repertoire_missing)
            ),
        ])

    def get_function_bar_fragments(self) -> StyleAndTextTuples:
        return [
            ("class:function-bar.key", "F1", handle_mouse_click(self.presenter.handle_start_training)),
            ("class:function-bar.label", f"{'Start training':<14}", handle_mouse_click(self.presenter.handle_start_training)),
        ]

    def get_function_bar_key_bindings(self) -> KeyBindings:
        """Creates the key bindings associated to the function bar fragments"""
        kb = KeyBindings()
        kb.add(Keys.F1)(handle_bound_key_pressed(self.presenter.handle_start_training))
        return kb
