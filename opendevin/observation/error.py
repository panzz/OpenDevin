from dataclasses import dataclass

from .base import Observation
from opendevin.schema import ObservationType


@dataclass
class AgentErrorObservation(Observation):
    """
    This data class represents an error encountered by the agent.
    """

    observation: str = ObservationType.ERROR

    @property
    def message(self) -> str:
        # return "Oops. Something went wrong: " + self.content
        return "哎呀。 出了些问题: " + self.content
