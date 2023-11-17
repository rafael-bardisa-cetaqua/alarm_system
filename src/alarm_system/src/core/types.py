
from datetime import datetime
from typing import Dict, List, Literal, Union

Alarm = Dict[Literal["plant_name", "event_name", "id_alarm", "last_alarm", "last_event", "flag_alarm", "type_alarm"], Union[str, int, float, datetime, bool]]
"""
An alarm is a dictionary that represents a trigger condition which should be notified if the condition is satisfied. Must have the following keys, but can be extended for other use cases:
:key plant_name: the related plant name. Should relate to a Plant
:key event_name: the alarm's identifying name
:key id_alarm: a unique id for the alarm
:key last_alarm: the last time the alarm was triggered and a notification was send
:key last_event: the timestamp of the latest processed event
:key flag_alarm: whether the alarm is currently triggered or not
:key type_alarm: the type of alarm. Should be used to dispatch the correct processing method for the alarm
"""


Plant = Dict[Literal["plant_name", "plant_name_proper", "events"], Union[str, int, float, datetime, List[str]]]
"""
A plant is a dictionary that represents a physical location.
:key plant_name: the plant name, intended to be unique
:key plant_name_proper: properly formatted plant name, to be used for notifications
:key events: the name of associated events with the given plant. Should relate to a list of Alarms
"""


Event = Dict[Literal["plant_name", "timestamp", "event_name", "ftp_inference", "ftp_original"], Union[str, int, float, datetime]]
"""
An event is a dictionary representing a recorded event. It is required that it has at least the following keys:
:key plant_name: the related plant name, Should relate to a Plant
:key timestamp: the time the event was recorded
:key event_name: the alarm name this event relates to. Should relate to an Alarm
"""


PlantContacts = Dict[Literal["plant_name", "email_contacts", "phone_contacts"], Union[str, List[str], List[int]]]
"""
This object represents the contacting information of a given plant name. Should only need the following keys:
:key plant_name: the related plant name. Should relate to a Plant
:key email_contacts: a list of email contacts (as strings) that should be notified when an event occurs in the given plant
:key phone_contacts: a list of phone contacts as integer numbers (prefix included) that should be notified when an event occurs in the given plant
"""
