from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.widgets import TextArea, VerticalLine, HorizontalLine

from .command_handler import CommandHandler


class WizWalkerCli(Application):
    def __init__(self, walker):
        self.walker = walker

        bindings = KeyBindings()

        @bindings.add("escape")
        @bindings.add("c-c")
        @bindings.add("c-q")
        def exit_app(event):
            """Closes the application"""
            event.app.exit()

        output_box = TextArea(style="class:output-field")
        status_box = TextArea(text="Current Status Box")
        input_box = CommandHandler(
            height=1,
            prompt="WizWalker> ",
            style="class:input-field",
            multiline=False,
            # wrap_lines=False,
            output=output_box,
            status=status_box,
            walker=walker,
            app=self,
            # accept_handler=accept_text
        )
        left_side = HSplit([input_box, HorizontalLine(), status_box])
        root = VSplit([left_side, VerticalLine(), output_box])
        layout = Layout(container=root)
        super().__init__(full_screen=True, key_bindings=bindings, layout=layout)

    def exit(self, *args) -> None:
        self.walker.close()

        super().exit(*args)
