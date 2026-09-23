from __future__ import annotations
from cli_chess.core.game import GameViewBase
from cli_chess.utils.ui_common import handle_mouse_click, NotationHelpContainer
from prompt_toolkit.widgets import TextArea, Box
from prompt_toolkit.layout import Window, Container, FormattedTextControl, VSplit, HSplit, VerticalAlign, ConditionalContainer, D
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import Condition
from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from cli_chess.core.game.openings_trainer import OpeningsTrainerPresenter


class OpeningsTrainerView(GameViewBase):
    def __init__(self, presenter: OpeningsTrainerPresenter):
        self.presenter = presenter
        self.input_field_container = self._create_input_field_container()
        self.notation_help = NotationHelpContainer()
        self.show_move_container = self._create_show_move_container()
        super().__init__(presenter)

    def _create_container(self) -> Container:
        main_content = Box(
            HSplit([
                VSplit([
                    self.board_output_container,
                    Box(HSplit([
                        self.material_diff_upper_container,
                        self.move_list_container,
                        self.material_diff_lower_container,
                    ]), padding=0, padding_top=1)
                ]),
                self.input_field_container,
                self.alert,
                self.show_move_container,
                self.notation_help,
            ]),
            padding=0
        )
        function_bar = HSplit([
            self._create_function_bar()
        ], align=VerticalAlign.BOTTOM)

        return HSplit([main_content, function_bar], key_bindings=self.get_key_bindings())

    def _create_input_field_container(self) -> TextArea:
        """Returns a TextArea to use as the move input field"""
        input_field = TextArea(height=D(max=1),
                               prompt="Move:",
                               style="class:move-input",
                               multiline=False,
                               wrap_lines=True,
                               focus_on_click=True)

        input_field.accept_handler = self._accept_input
        return input_field

    def _accept_input(self, input: Buffer) -> None: # noqa
        """Accept handler for the input field"""
        self.presenter.user_input_received(input.text)
        self.input_field_container.text = ''

    def _create_show_move_container(self) -> ConditionalContainer:
        """Creates the toggleable container used to reveal the expected move and
           prompt the user to acknowledge it before training continues
        """
        return ConditionalContainer(
            Window(FormattedTextControl(self._get_show_move_fragments), always_hide_cursor=True, wrap_lines=True),
            filter=Condition(self.presenter.is_move_revealed)
        )

    def _get_show_move_fragments(self) -> StyleAndTextTuples:
        """Returns the text fragments used to display the revealed move"""
        return [
            ("class:label", f"Move: {self.presenter.get_revealed_move_san()}\n"),
            ("class:label", "Understood? "),
            ("class:function-bar.label", "[Yes]", handle_mouse_click(self.presenter.acknowledge_revealed_move)),
        ]

    def _show_move_fb_fragments(self) -> Tuple:
        """Returns the function bar fragments for revealing the expected move"""
        return (
            ("class:function-bar.key", "F2", handle_mouse_click(self.presenter.reveal_move)),
            ("class:function-bar.label", f"{'Show move':<11}", handle_mouse_click(self.presenter.reveal_move)),
            ("class:function-bar.spacer", " "),
        )

    def _exit_fb_fragments(self) -> Tuple:
        """Returns the function bar fragments for exiting the trainer. Overrides
           the base class' F8 binding, as this view uses F4 for exit
        """
        return (
            ("class:function-bar.key", "F4", handle_mouse_click(self.presenter.exit)),
            ("class:function-bar.label", f"{'Exit':<11}", handle_mouse_click(self.presenter.exit)),
            ("class:function-bar.spacer", " "),
        )

    def _notation_help_fb_fragments(self) -> Tuple:
        """Returns the function bar fragments for toggling the notation cheat sheet"""
        return (
            ("class:function-bar.key", "F5", handle_mouse_click(self.notation_help.toggle)),
            ("class:function-bar.label", f"{'Notation':<11}", handle_mouse_click(self.notation_help.toggle)),
            ("class:function-bar.spacer", " "),
        )

    def _create_function_bar(self) -> VSplit:
        """Creates the views function bar. F3 is intentionally unused"""
        def _get_function_bar_fragments() -> StyleAndTextTuples:
            fragments = ([])
            fragments.extend(self._flip_board_fb_fragments())

            if not self.presenter.is_training_complete():
                fragments.extend(self._show_move_fb_fragments())

            fragments.extend(self._exit_fb_fragments())

            if not self.presenter.is_training_complete():
                fragments.extend(self._notation_help_fb_fragments())

            return fragments

        return VSplit([
            Window(FormattedTextControl(_get_function_bar_fragments)),
        ], height=D(max=1, preferred=1))

    def get_key_bindings(self) -> "_MergedKeyBindings":  # noqa: F821
        """Returns the key bindings for this container. F3 is intentionally unused"""
        bindings = KeyBindings()

        @bindings.add(Keys.F1, eager=True)
        def _(event): # noqa
            self.presenter.flip_board()

        @bindings.add(Keys.F2, filter=~Condition(self.presenter.is_training_complete), eager=True)
        def _(event): # noqa
            self.presenter.reveal_move()

        @bindings.add(Keys.Enter, filter=Condition(self.presenter.is_move_revealed), eager=True)
        def _(event): # noqa
            self.presenter.acknowledge_revealed_move()

        @bindings.add(Keys.F4, eager=True)
        def _(event): # noqa
            self.presenter.exit()

        @bindings.add(Keys.F5, filter=~Condition(self.presenter.is_training_complete), eager=True)
        def _(event): # noqa
            self.notation_help.toggle()

        return merge_key_bindings([bindings, self.move_list_container.key_bindings])
