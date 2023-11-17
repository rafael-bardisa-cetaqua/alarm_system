from abc import ABC, abstractmethod
import logging
from typing import Union
from ..types import Alarm, Plant, Event, PlantContacts


class INotifier(ABC):
    """
    This interface manages the ways to notify relevant contacts of a given event
    """
    logger: logging.Logger

    @abstractmethod
    def notify_trigger(self, alarm: Alarm, plant: Plant, contacts: PlantContacts, event: Event, message_label: Union[str, bool]) -> bool:
        """
        notify contacts of plant that an event triggered given alarm
        :param alarm: The related triggered alarm
        :param plant: the related plant where the alarm got triggered
        :param contacts: dict of contacts (email and sms) to notify
        :param event: the event that triggered the alarm
        :param message_label: some use cases require an alarm to dispatch different messages given different conditions (e.g, when first triggered and then when no longer active). This label is used to identify the type of message to return
        """
