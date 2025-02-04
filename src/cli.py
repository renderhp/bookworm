import shlex

from prompt_toolkit import PromptSession

from commands.command_registry import CommandRegistry
from commands.setup import Setup


class CLI:
    def __init__(self):
        self.setup_commands()

    def setup_commands(self) -> None:
        self.command_registry = CommandRegistry()
        self.command_registry.register_command("setup", Setup)

    def run(self):
        session = PromptSession()

        try:
            while True:
                user_input = session.prompt("> ")
                args = shlex.split(user_input)
                command, args = args[0], args[1:]
                self.command_registry.execute_command(command, *args)
        except KeyboardInterrupt:
            print("Hope you found what you were looking for :)")
