from prompt_toolkit import prompt
from rich import print
from prompt_toolkit.shortcuts import radiolist_dialog
from constants import (
    PROVIDER_OPENAI,
    SETTINGS_PREFERRED_PROVIDER,
    SETTINGS_PROVIDER_KEY,
)
from utils.db_utils import create_db, set_setting


from .command_base import CommandBase

DB_PATH = "bookworm.db"


class Setup(CommandBase):
    def help(self) -> str:
        return "Initial setup of the DB, keys, etc."

    def execute(self, *args) -> None:
        print("1) Create the DB")
        create_db(*args)
        print("2) Set up an API key")
        self.provide_keys()
        print("[green]Setup Succesful[/green]")

    def provide_keys(self) -> None:
        values = [
            (PROVIDER_OPENAI, "Open AI"),
        ]
        service_provider = radiolist_dialog(
            title="Select an option",
            text="Which service provider do you want to use?",
            values=values,
        ).run()
        api_key = prompt("Please provide the API key: ")
        set_setting(SETTINGS_PREFERRED_PROVIDER, service_provider)
        set_setting(SETTINGS_PROVIDER_KEY, api_key)
        print("[green]Succesfully stored the provider and the key[/green]")
