import logging
from .interfaces.connector import IConnector
from .interfaces.notifier import INotifier
from .interfaces.processor import IProcessor

# TODO not thread safe, not urgent but keep in mind until perfect solution is found
from copy import deepcopy


class Orchestrator:
    """
    Controls the flow of information between all parts of the AlarmSystem. Parts can be individually replaced as long as the implement the corresponding interfaces.
    """
    logger: logging.Logger

    def __init__(self, connector: IConnector, processor: IProcessor, notifier: INotifier, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.debug(f"setting up Orchestrator")

        self.connector = connector
        self.processor = processor
        self.notifier = notifier

    def execute(self):
        self.logger.debug(f"collecting system data")
        alarms, plants, contacts, events = self.connector.load_system_data()

        # str() deberia ser redundante, pero así el pylance se entera que tiene que ser str por la fuerza
        alarms_indexed = {str(alarm["event_name"]): alarm for alarm in alarms}

        self.logger.debug(f"indexing contacts...")
        contacts_indexed = {contact["plant_name"]: contact for contact in contacts}

        self.logger.debug(f"indexing plants...")
        plants_indexed = {str(plant["plant_name"]): plant for plant in plants}

        self.logger.debug(f"sorting events over timestamp...")
        events = sorted(events, key= lambda event: event["timestamp"])

        self.logger.debug(f"indexing events based on alarms...")
        indexed_events_by_alarm = {str(alarm["event_name"]): [event for event in events if str(event["event_name"]) == alarm["event_name"] and str(event["plant_name"]) == alarm["plant_name"]] for alarm in alarms}

        for alarm in alarms:
            plant = plants_indexed[alarm["plant_name"]]
            plant_contacts = contacts_indexed[alarm["plant_name"]]
            alarm_events = indexed_events_by_alarm[alarm["event_name"]]

            for event in alarm_events:
                alarm_before_event = deepcopy(alarm)
                event_result = self.processor.process_event(alarm, plant, event)

                if not event_result:
                    continue

                self.notifier.notify_trigger(alarm_before_event, plant, plant_contacts, event, event_result)
        
        self.logger.debug(f"updating alarm information in remote...")
        self.connector.update_system_alarms(alarms)
