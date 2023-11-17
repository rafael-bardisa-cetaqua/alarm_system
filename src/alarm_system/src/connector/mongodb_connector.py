import logging
from datetime import datetime
from typing import List, Tuple
from ..core.interfaces.connector import IConnector
from ..core.types import Alarm, Event, Plant, PlantContacts

from pymongo import MongoClient

from ..connector.types import ConnectorConfig as Config


class MongoDBConnector(IConnector):
    config: Config

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.debug(f"setting up MongoDBLoader with config: {config}")
        self.config = config

    def load_system_data(self) -> Tuple[List[Alarm], List[Plant], List[PlantContacts], List[Event]]:
        mongo_db = MongoClient(self.config['url'])[self.config['db_name']]

        alarm_collection = mongo_db[self.config['alarm_collection']]
        plant_collection = mongo_db[self.config['plant_collection']]
        event_collection = mongo_db[self.config['event_collection']]
        contacts_collection = mongo_db[self.config['contacts_collection']]

        self.logger.debug(f"collecting alarms from mongodb")
        alarms: List[Alarm] = [alarm for alarm in alarm_collection.find()]
        self.logger.debug(f"collected alarms: {len(alarms)}")

        self.logger.debug(f"collecting plants from mongodb")
        plants: List[Plant] = [plant for plant in plant_collection.find()]
        self.logger.debug(f"collected plants: {len(plants)}")

        self.logger.debug(f"collecting contacts from mongodb")
        contacts: List[PlantContacts] = [contact for contact in contacts_collection.find()]
        self.logger.debug(f"collected contacts for plants: {len(contacts)}")

        events: List[Event] = []
        # get only newer events
        for alarm in alarms:
            self.logger.debug(f"collecting latest {alarm['event_name']} events")

            try:
                alarm['last_event']
            except KeyError:
                self.logger.warning(f"alarm {alarm['event_name']} has no recorded last event. Collecting entire collection...")
                alarm['last_event'] = datetime.min


            type_events: List[Event] = [event for event in event_collection.find({"event_name": alarm['event_name'], "timestamp": {"$gt": alarm['last_event']}})]
            self.logger.debug(f"collected {len(type_events)} {alarm['event_name']} events")

            events.extend(type_events)

        self.logger.debug(f"collected events: {len(events)}")

        return alarms, plants, contacts, events


    def update_system_alarms(self, alarms: List[Alarm]) -> bool:
        mongo_db = MongoClient(self.config['url'])[self.config['db_name']]

        alarm_collection = mongo_db[self.config['alarm_collection']]

        for alarm in alarms:
            alarm_collection.update_one({"id_alarm": alarm['id_alarm']}, {"$set": alarm})