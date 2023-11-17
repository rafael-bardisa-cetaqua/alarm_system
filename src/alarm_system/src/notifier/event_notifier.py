from collections import defaultdict
import logging
from typing import Dict, Union
from ..core.interfaces.notifier import INotifier
from ..core.types import Alarm, Event, Plant, PlantContacts
from .types import MessageBuilder, NotifierConfig as Config
from mailer import EmailAPI
from .sms_alerter import SMSAlert


#TODO sms for phone contacts
class EventNotifier(INotifier):
    logger: logging.Logger
    message_builder_dispatcher: Dict[str, Dict[Union[str, bool], MessageBuilder]]

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.debug(f"setting up EventNotifier")
        self.mailer = EmailAPI(sender_addr=config['sender_email'], sender_pass=config['sender_password'], logger=self.logger)
        self.sms_alerter = SMSAlert(sender=config['sender_sms'], token=config['token_sms'], pemfile=config['pemfile_sms'], logger=self.logger)
        self.message_builder_dispatcher = defaultdict(dict)


    def notify_trigger(self, alarm: Alarm, plant: Plant, contacts: PlantContacts, event: Event, message_label: Union[str, bool]) -> bool:
        subject = f"Alarm {alarm['event_name']} triggered in {plant['plant_name_proper']}"

        self.logger.debug(f"dispatching message builder for alarm {alarm['type_alarm']}. message label: {message_label}")
        try:
            body_builder = self.message_builder_dispatcher[alarm['type_alarm']][message_label]
            body = body_builder(alarm, event, plant, message_label, self.logger)
        except KeyError:
            self.logger.error(f"No function registered to create a message for alarm type {alarm['type_alarm']}. Skipping...")
            return False

        attachments: Dict[str, str] = {}

        try:
            inference_extension = event['ftp_inference'].split(".")[-1]
            attachments[event['ftp_inference']] = f"inference.{inference_extension}"
        except KeyError:
            self.logger.warning(f"No information found about inference image")

        try:
            original_extension = event['ftp_original'].split(".")[-1]
            attachments[event['ftp_original']] = f"original.{original_extension}"
        except KeyError:
            self.logger.warning(f"No information found about original image")

        email_recipients = contacts['email_contacts']

        if email_recipients:
            self.mailer.send_email(to=email_recipients, subject=subject, body=body, attachments=attachments)

        phone_recipients = contacts['phone_contacts']

        if phone_recipients:
            self.sms_alerter.send_sms(message=body, recipients=phone_recipients)

        return True
    

    def register_message_builder(self, alarm_type: str, message_builder: MessageBuilder, *, message_label: Union[str, bool]=True) -> None:
        """
        registers a function to build the message of a given alarm type
        """
        self.logger.debug(f"registered message builder: {message_builder} for alarm type {alarm_type} and result {message_label}")
        self.message_builder_dispatcher[alarm_type][message_label] = message_builder


    def enable_sftp(self, host: str, sftp_user: str, sftp_pass: str, sftp_pk_path: str, label: str="default") -> bool:
        """
        enables sftp connection for the mailer module
        """
        return self.mailer.enable_sftp(host, sftp_user, sftp_pass, sftp_pk_path, label=label)
