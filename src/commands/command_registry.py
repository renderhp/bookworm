from .command_base import CommandBase
from rich import print
from rich.table import Table
from rich.panel import Panel


class CommandRegistry:
    def __init__(self):
        self._registered_commands = {}

    def register_command(self, name: str, command: CommandBase) -> None:
        self._registered_commands[name] = command

    def execute_command(self, name: str, *args) -> None:
        if name == "help":
            self.print_commands()
            return
        if name not in self._registered_commands:
            print(
                Panel(
                    "[red]Command not found![/red]\n\nAvailable commands are listed below:",
                    border_style="red",
                    title="Error",
                )
            )
            self.print_commands()
            return
        cmd = self._registered_commands[name]()
        cmd.execute(*args)

    def print_commands(self) -> None:
        table = Table(
            title="Available Commands",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            expand=True,
        )

        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Help", style="green")

        table.add_row("help", "Show this help message")

        for name, command in self._registered_commands.items():
            cmd: CommandBase = command()
            help_text = cmd.help()
            table.add_row(name, help_text)

        print(table)
