import logging
from typing import List
import requests

class SMSAlert():
    """
    send sms alerts to phone numbers using gateway api
    """

    sender: str
    token: str
    pemfile: str

    def __init__(self, sender: str, token: str, pemfile: str, logger: logging.Logger) -> None:
        """
        :param sender: sender name, like "Cetaqua"
        :param token: token used for the sms api
        :param pemfile: path to the api public certificate (a pem file)
        :param logger: a logger
        """
        
        self.logger = logger
        self.sender = sender
        self.token = token
        self.pemfile = pemfile

        self.logger.debug(f"SMS service initialized")

    def send_sms(self, message: str, recipients: List[int]):

        payload = {
            "sender": self.sender,
            "message": message,
            "recipients": [
                {"msisdn": recipient_number}
                for recipient_number in recipients
            ],
        }

        self.logger.debug(f"sending sms alert: {payload}")

        try:
            resp = requests.post(
                "https://gatewayapi.com/rest/mtsms",
                json=payload,
                auth=(self.token, ""),
                verify=self.pemfile
            )

            resp.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error(f"could not send sms alert to recipients. Reason:\n{e}")