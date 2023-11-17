from abc import ABC, abstractmethod
import logging
from typing import List, Tuple

from ..types import Alarm, Plant, Event, PlantContacts

class IConnector(ABC):
    """
    This interface manages connecting to a data source for reading and writing event data
    """
    logger: logging.Logger

    @abstractmethod
    def load_system_data(self) -> Tuple[List[Alarm], List[Plant], List[PlantContacts], List[Event]]:
        """
        loads alarm, plant, contact and event data for the alarm system
        """

    @abstractmethod
    def update_system_alarms(self, alarms: List[Alarm]) -> bool:
        """
        update list of alarms for future reuse
        :param alarms: the alarms to update in a remote database
        :returns: bool whether the update was successful or not
        """
