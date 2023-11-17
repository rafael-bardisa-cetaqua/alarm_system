
from collections import defaultdict
import logging
from typing import Dict, List, Union
from typing_extensions import deprecated
from ..core.interfaces.processor import IProcessor
from ..core.types import Alarm, Event, Plant

from .types import AlarmProcessor

class EventProcessor(IProcessor):
    logger: logging.Logger
    dispatcher: Dict[str, AlarmProcessor]

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.debug(f"setting up EventProcessor")
        self.dispatcher = {}

    @deprecated("This function requires understanding the internal implementation to call correctly. Consider refactoring to use process_event instead.")
    def process_alarms(self, alarms: List[Alarm], plants: Dict[str, Plant], events: Dict[str, List[Event]]) -> Dict[str, List[Union[str, None]]]:
        result = defaultdict(list)
        self.logger.info(f"alarms before processing: {alarms}")

        for idx, alarm in enumerate(alarms):
            alarm_name = alarm['event_name']
            self.logger.debug(f"processing alarm {alarm_name}")

            self.logger.debug(f"gathering events")
            alarm_events = events[alarm_name]
            self.logger.debug(f"dispatching processor function")

            try:
                processor = self.dispatcher[alarm['type_alarm']]
            except KeyError:
                self.logger.warning(f"no processor defined for {alarm['type_alarm']} alarms. Skipping...")
                continue

            for jdx, event in enumerate(alarm_events):
                self.logger.debug(f"processing event {jdx + 1}")
                result[alarm_name].append(processor(alarm, event, self.logger))
                alarm['last_event'] = event['timestamp']

            # it is possible that no new events have been registered, in which case no update is needed
            if alarm_events:
                alarm['last_event'] = alarm_events[-1]['timestamp']

            alarms[idx] = alarm

        self.logger.info(f"alarms after processing: {alarms}")

        self.logger.debug(f"triggered events: {result}")
        return result
    

    def process_event(self, alarm: Alarm, plant: Plant, event: Event) -> Union[str,None]:
        alarm_name = alarm['event_name']
        self.logger.debug(f"processing alarm {alarm_name}")

        try:
            processor = self.dispatcher[alarm['type_alarm']]
            alarm['last_event'] = max(event['timestamp'], alarm['last_event'])  # max ensures timestamp is the last event seen
        except KeyError:
            self.logger.warning(f"no processor defined for {alarm['type_alarm']} alarms. Skipping...")
            return None
        
        result = processor(alarm, event, self.logger)

        return result

    
    def register_processor(self, alarm_type: str, processor: AlarmProcessor):
        """
        register a function to be used for a given alarm type
        """
        self.logger.debug(f"registered processor: {processor} for alarm type {alarm_type}")
        self.dispatcher[alarm_type] = processor
        