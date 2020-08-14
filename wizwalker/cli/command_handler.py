from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.widgets import TextArea

from ..wad import Wad


class CommandHandler(TextArea):
    def __init__(self, *args, **kwargs):
        self.output = kwargs.pop("output")
        self.status = kwargs.pop("status")
        self.walker = kwargs.pop("walker")
        self.app = kwargs.pop("app")
        super().__init__(*args, **kwargs)
        self.accept_handler = self.process_command
        self.status_keys = {}

    def process_command(self, buffer: Buffer):
        text_string = buffer.text
        cmd, *args = text_string.split(" ")
        try:
            command = self.commands[cmd]
        except KeyError:
            self.write_output(f'Command "{cmd}" not found.\n')
            return

        self.write_output(f"Command: {cmd} {' '.join(args)}")
        command(args)
        self.write_output("\n")

    def write_output(self, text: str):
        to_write = self.output.text + text + "\n"
        self.output.buffer.document = Document(
            text=to_write, cursor_position=len(to_write)
        )

    def update_status(self):
        status_message = "\n".join([f"{key}: {value}" for key, value in self.status_keys.items()])
        self.status.buffer.text = status_message

    @property
    def commands(self):
        if hasattr(self, "_cmds"):
            return self._cmds

        cmds = {}
        for item in dir(self):
            if item.startswith("command_"):
                cmds.update(
                    {
                        item.replace("command_", ""): getattr(self, item)
                    }
                )

        self._cmds = cmds
        return cmds

    def command_test(self, args):
        """Test command"""
        self.write_output(f"Test!! {args=}")

    def command_help(self, args):
        """Shows this message"""
        final = ""
        for name, callback in self.commands.items():
            final += name
            if callback.__doc__ is not None:
                final += " - "
                final += callback.__doc__
            final += "\n"

        self.write_output(final.strip("\n"))

    def command_attach(self, args):
        """Attach to current wiz clients"""
        self.walker.get_clients()
        self.status_keys["Connected clients"] = len(self.walker.clients)
        self.update_status()
        self.write_output("Attached")

    def command_inject(self, args):
        """Inject code to get current cords, enables cords command"""
        for client in self.walker.clients:
            client.memory.start_cord_thread()

        self.write_output("Injected cords")

    def command_cords(self, args):
        """Get cords of all clients"""
        for idx, client in enumerate(self.walker.clients):
            self.write_output(f"client-{idx}: {client.xyz}")

    def command_quest(self, args):
        """Gets cords of quests"""
        for idx, client in enumerate(self.walker.clients):
            self.write_output(f"client-{idx}: {client.quest_xyz}")

    def command_send(self, args):
        """send a key to a client
        EX:
        send 1 w 2
        where 1 is the client index, w is the key, and 2 is the number of seconds to send for
        note that letters must be caps
        """
        try:
            client, key, seconds = args
        except ValueError:
            self.write_output("Not enough or too many args")
            return

        try:
            self.walker.clients[int(client)].keyboard.send_key(key, float(seconds))
        except IndexError:
            self.write_output(f"Client with index {client} not found")
        else:
            self.write_output(f"Sent {key} for {seconds} seconds")

    def command_wad(self, args):
        """
        extract a file from a wad archive
        EX:
        wad WizardCity-WC_Streets-WC_Unicorn.wad Compass.xml
        """
        try:
            wad_name, file_name = args
        except ValueError:
            self.write_output("Not enough or too many args")
            return

        wad = Wad(wad_name)
        file_data = wad.get_file(file_name)

        with open(file_name, "wb+") as fp:
            fp.write(file_data)

    def command_exit(self, args):
        """Exit cli"""
        self.app.exit()

