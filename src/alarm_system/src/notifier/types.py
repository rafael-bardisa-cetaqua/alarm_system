import logging
from typing import Callable, Dict, Literal


from ..core.types import Alarm, Event, Plant


NotifierConfig = Dict[Literal["sender_email", "sender_password", "sender_sms", "token_sms", "pemfile_sms"], str]
"""
configuration object for event notifier
"""

MessageBuilder = Callable[[Alarm, Event, Plant, str, logging.Logger], str]
"""
anonymous function for message building, to be used for specific alarm types
"""
