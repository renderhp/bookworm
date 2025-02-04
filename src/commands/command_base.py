from abc import ABC, abstractmethod


class CommandBase(ABC):
    @abstractmethod
    def help(self) -> str:
        pass

    @abstractmethod
    def execute(self, *args) -> None:
        pass
