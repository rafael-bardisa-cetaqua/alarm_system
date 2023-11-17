import logging
from typing import Callable, Union


from ..core.types import Alarm, Event


AlarmProcessor = Callable[[Alarm, Event, logging.Logger], Union[str, bool]]
"""
Signature of an alarm processor. Must be a function like foo(x: Alarm, y: Event, z: logging.Logger) -> bool

The alarm parameter must be modified inplace when an event would warrant it (i.e, if an event would trigger the alarm, it must be annotated with x["flag_alarm"] = True)
The event parameter must be read only, any method conforming to this signature should never change a value of the event parameter
The logger parameter is used to debug the execution of the function once inside the system

:return: returns whether the event should be notified
"""
