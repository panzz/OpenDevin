from dataclasses import dataclass

from .base import Observation
from opendevin.schema import ObservationType


@dataclass
class FileReadObservation(Observation):
    """
    This data class represents the content of a file.
    """

    path: str
    observation: str = ObservationType.READ

    @property
    def message(self) -> str:
        # return f"I read the file {self.path}."
        return f"我读了文件 {self.path}."


@dataclass
class FileWriteObservation(Observation):
    """
    This data class represents a file write operation
    """

    path: str
    observation: str = ObservationType.WRITE

    @property
    def message(self) -> str:
        # return f"I wrote to the file {self.path}."
        return f"我写入文件 {self.path}."
