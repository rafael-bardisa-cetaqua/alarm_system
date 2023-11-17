from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Union
from ..types import Alarm, Plant, Event


class IProcessor(ABC):
    """
    This interface manages processing the bulk of the data
    """
    logger: logging.Logger

    @abstractmethod
    def process_event(self, alarm: Alarm, plant: Plant, event: Event) -> Union[str, None]:
        """
        process an event and immediately return the result
        """
