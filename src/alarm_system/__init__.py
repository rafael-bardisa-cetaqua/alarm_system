import logging
from typing import Dict, Literal, Union

from . import types

from .src.processor.event_processor import EventProcessor

from .src.notifier.event_notifier import EventNotifier

from .src.connector.mongodb_connector import MongoDBConnector
from .src.core.orchestrator import Orchestrator

__version__ = "0.1.0"

"""
This module contains the alarm system default implementation, as well as interfaces to build a custom one. More information in the README file
"""

AlarmSystemConfig = Dict[Literal["url", "db_name", "alarm_collection", "plant_collection", "event_collection", "contacts_collection", "sender_email", "sender_password", "sender_sms", "token_sms", "pemfile_sms"], str]

class AlarmSystem():
    """
    Default implementation of Lab CV AlarmSystem. Initializes internal modules with the default implementations provided in the repository
    """
    def __init__(self, config: AlarmSystemConfig, logger: logging.Logger = logging.Logger(__name__)):
        self.logger = logger

        processor = EventProcessor(self.logger)

        connector_config_keys = ["url", "db_name", "alarm_collection", "plant_collection", "event_collection", "contacts_collection"]
        connector_config = {key: config[key] for key in connector_config_keys}
        connector = MongoDBConnector(connector_config, self.logger)

        notifier_config_keys = ["sender_email", "sender_password", "sender_sms", "token_sms", "pemfile_sms"]
        notifier_config = {key: config[key] for key in notifier_config_keys}
        notifier = EventNotifier(notifier_config, logger)

        self.orchestrator = Orchestrator(connector, processor, notifier, self.logger)

        self.logger.info(f"AlarmSystem created")


    def execute(self):
        """
        execute the alarm system
        """
        self.orchestrator.execute()


    def register_processor(self, alarm_type: str, processor_func: types.AlarmProcessor) -> None:
        """
        register a processor function to be used for a given alarm type
        """
        processor: EventProcessor = self.orchestrator.processor
        processor.register_processor(alarm_type, processor_func)


    def register_message_builder(self, alarm_type: str, message_builder_func: types.MessageBuilder, *, message_label: Union[str, bool]=True) -> None:
        """
        register a message builder to be used for a given alarm type
        """
        notifier: EventNotifier = self.orchestrator.notifier
        notifier.register_message_builder(alarm_type, message_builder_func, message_label=message_label)


    def enable_sftp(self, host: str, sftp_user: str, sftp_pass: str, sftp_pk_path: str, label: str="default") -> bool:
        """
        enables sftp connection for file attachments
        """
        notifier: EventNotifier = self.orchestrator.notifier

        return notifier.enable_sftp(host, sftp_user, sftp_pass, sftp_pk_path, label=label)