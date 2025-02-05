from openai import OpenAI
from .command_base import CommandBase
from utils.db_utils import get_setting
from constants import SETTINGS_PROVIDER_KEY


class Ask(CommandBase):
    def __init__(self):
        super().__init__()
        self.api_key = get_setting(SETTINGS_PROVIDER_KEY)

        if not self.api_key:
            raise Exception("API key is not set")

    def help(self) -> str:
        return "Ask a question"

    def execute(self, *args) -> None:
        client = OpenAI(api_key=self.api_key)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": "write a haiku about ai"}],
        )

        print(completion.choices[0].message.content)
