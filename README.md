# Alarm System (Lab CV)
Alarm management module that processes different alarms and events and notifies the generated alerts via gmail. You can also [customize the system with your own modules](README#Building%20your%20own%20Alarm%20System).

---
## Installation
You can install the package directly with pip:
```bash
pip install "alarm_system @ git+https://github.com/rafael-bardisa-cetaqua/alarm_system.git"
```
Or you can add it as a requirement on a pipfile:
```toml
[packages]
alarm_system = {git = "https://github.com/rafael-bardisa-cetaqua/alarm_system.git"}
```

If you need a specific version, you can specify which tag (or branch, same syntax) to download:
```bash
pip install "alarm_system @ git+https://github.com/rafael-bardisa-cetaqua/alarm_system.git@0.1.0"
```

```toml
[packages]
alarm_system = {git = "https://github.com/rafael-bardisa-cetaqua/alarm_system.git", ref="0.1.0"}
```
If you do not specify a tag or a branch, pip will retrieve [the latest commit in the main branch](https://github.com/rafael-bardisa-cetaqua/alarm_system).

---
## Usage
To create an instance of the system, pass in the required configuration options:
```python
from alarm_system import AlarmSystem


url = os.getenv("MONGODB_URL")
db_name = os.getenv("MONGODB_DB_NAME")
alarm_collection = os.getenv("ALARM_COLLECTION")
plant_collection = os.getenv("PLANT_COLLECTION")
event_collection = os.getenv("EVENT_COLLECTION")
contacts_collection = os.getenv("CONTACTS_COLLECTION")

sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

sender_sms = os.getenv("SENDER_SMS")
token_sms = os.getenv("TOKEN_SMS")
pemfile_sms = os.getenv("PEMFILE_SMS")

config = {
	"url": url,
	"db_name": db_name,
	"alarm_collection": alarm_collection,
	"plant_collection": plant_collection,
	"event_collection": event_collection,
	"contacts_collection": contacts_collection,
	"sender_email": sender_email,
	"sender_password": sender_password,
	"sender_sms": sender_sms,
	"token_sms": token_sms,
	"pemfile_sms": pemfile_sms
}

alarm_system = AlarmSystem(config)
```
Where:
- `url` is a `mongodb` cluster URL.
- `db_name` is the database name within the `MongoDB` cluster.
- `alarm_collection`, `plant_collection`, `event_collection` and `contacts_collection` are the collection names where the respective data is located.
- `sender_email` is the email adress used to notify of triggered alerts.
- `sender_password` is the password to log in to the sender email.
- `sender_sms` is the name to be shown when sending an sms alert
- `token_sms` is a valid token for the sms api
- `pemfile_sms` is the path to the public certificate file of the api webpage, to avoid MITM attacks

Each data point in each `MongoDB` collection must store several required fields, which you can read about [here](README#MongoDB%20data).

[Processing](README#AlarmProcessors) and [message creation](README#MessageBuilders) functions need to be registered before using the system, like so:
```python
from alarm_system.types import Alarm, Event, Plant


def my_alarm_processor(alarm: Alarm, event: Event, logger: logging.Logger) -> Union[str, bool]:
	...


def my_message_builder(alarm: Alarm, event: Event, plant: Plant, message_label: Union[str, bool], logger: logging.Logger) -> str:
	...


def my_activation_message_builder(alarm: Alarm, event: Event, plant: Plant, message_label: Union[str, bool], logger: logging.Logger) -> str:
	...


# register function to process threshold alarms
alarm_system.register_processor("threshold", my_alarm_processor)

# my_message_builder will be used when my_alarm_processor returns True or "reminder"
alarm_system.register_message_builder("threshold", my_message_builder)
alarm_system.register_message_builder("threshold", my_message_builder, message_label="reminder")

# my_activation_message_builder will be used when my_alarm_processor returns "activation"
alarm_system.register_message_builder("threshold", my_activation_message_builder, message_label="activation")


# the alarm system can now be run
alarm_system.execute()
```

You can read about the system types [here](README#System%20types).

### MongoDB data
By default, the AlarmSystem will read data from a `MongoDB` database. Different collections will store different types of dictionary-like data, and will require a set of fields to be present.
#### Alarms collection
The alarms collection stores alarm representations. These relate directly to the state of the alarm at a given time. An alarm document must have the following fields:
```javascript
{
	"plant_name": str,
	"event_name": str,
	"id_alarm": number,
	"last_alarm": datetime,
	"last_event": datetime,
	"flag_alarm": bool,
	"type_alarm": str
}
```
Alarms can have additional fields to provide flexibility for different use cases.
#### Events collection
The events collection stores events of different plants. An event document must have at least the following fields:
```javascript
{
	"plant_name": str,
	"timestamp": datetime,
	"event_name": str // akin to event type, for classification
}
```
Events can also store additional information in extra fields. 
#### Plants collection
This collection lists the different plants the system can operate on and the events relevant for each plant. A plants document must have the following fields:
```javascript
{
	"plant_name": str,
	"plant_name_proper": str,
	"events": [str] // list of event names related to the plant
}
```
Plants allow the system to group alarms and events related to a specific plant, as well as the contacts (email addresses and phone numbers) of people interested in monitoring the alarms for that plant.
#### Contacts collection
The contacts collection stores the list of contacts (phone numbers and/or email addresses) for a given plant. A contacts document must have the following fields:
```javascript
{
	"plant_name": str,
	"email_contacts": [str],
	"phone_contacts": [number]
}
```

### System types
The `Alarm`, `Event`, `Plant` and `PlantCollection` classes defined in the `types` submodule are actually dictionaries, with the constraint that they should at least implement a set of keys, different for each type:
```python
Alarm = Dict[Literal["plant_name", "event_name", "id_alarm", "last_alarm", "last_event", "flag_alarm", "type_alarm"], Union[str, int, float, datetime, bool]]

Plant = Dict[Literal["plant_name", "plant_name_proper", "events"], Union[str, int, float, datetime, List[str]]]

Event = Dict[Literal["plant_name", "timestamp", "event_name"], Union[str, int, float, datetime]]

PlantContacts = Dict[Literal["plant_name", "email_contacts", "phone_contacts"], Union[str, List[str], List[int]]]
```

When creating the functions for the system, read these types as "dictionaries who guarantee the existence of at least these fields". This model allows for easy extension depending on a concrete alarm type while providing linting within IDEs like `VSCode` for the common fields in the given class.
### AlarmProcessors
AlarmProcessors are functions that determine whether a recorded event should trigger an alert based on the current alarm state. They are responsible for updating the alarm state and returning a label that indicates whether the event should be notified and, if so, which type of message should be dispatched.

The signature for an alarm processor must be as follows:
```python
def my_alarm_processor(alarm: Alarm, event: Event, logger: logging.Logger) -> Union[str, bool]:
	...
```
Where:
- The `alarm` parameter is a dictionary representing the current state of the alarm. The processor function is expected to modify this dictionary to update the alarm's state after processing the event.
- The `event` parameter is a dictionary containing the details of the recorded event. It is crucial to treat this parameter as read-only to avoid unintentionally modifying it in-place.
- The `logger` parameter is a logging object that can be used to log debug messages or other information during the processing of the alarm, which can be helpful for troubleshooting or monitoring purposes.
- The function must return either a string or a boolean value. This return value is treated as a label for the system to dispatch the appropriate message for alarms that warrant different relevant events.

A complete processing function could look like this:
```python
def process_continuous_alarm(alarm: Alarm, event: Event, logger: logging.Logger) -> Union[str, bool]:
	"""
	process a continuous alarm and return a label indicating whether to notify the event
	and, if so, which type of message to dispatch.
	"""
	event_triggered = event["event_percentage"] >= alarm["threshold"]
	alarm_active = alarm["flag_alarm"]
	long_time_since_event = event["timestamp"] - alarm["last_alarm"] > datetime.timedelta(minutes=alarm["reminder_threshold"])
	
	# logging to make sure parameters are as expected
	logger.debug(f"alarm triggered by event? {event_triggered}")
	logger.debug(f"alarm already active? {alarm_active}")
	logger.debug(f"time ince last alarm activation? {long_time_since_event}")
	
	# updating alarm state inplace
	alarm['flag_alarm'] = event_triggered
	
	if not event_triggered:
		return False
	if not alarm_active:
		alarm['last_alarm'] = event['timestamp']
		return False
	if not long_time_since_event:
		return "reminder"
	
	alarm['last_alarm'] = event['timestamp']
	# if we return true, this event must be notified
	return True
```

The function:
- Updates the `alarm` state
- Does not modify the `event` parameter
- Returns either a `str` label or a `bool` value. The system will not notify of events that return [falsy values](https://stackoverflow.com/a/39984051/12881307).

Once defined, the alarm processor function must be registered with the system as shown in the [usage](README#Usage) section.
### MessageBuilders
These functions are responsible of building the message an alert would send to the registered recipients. Their signature must be as follows:
```python
def my_message_builder(alarm: Alarm, event: Event, plant: Plant, message_label: Union[str, bool], logger: logging.Logger) -> str:
	...
```
Where:
- The `alarm` parameter is a dictionary representing the current state of the alarm.
- The `event` parameter is a dictionary containing the details of the recorded event that triggered the alarm.
- The `plant` parameter is a dictionary containing information about the plant associated with the alarm and event.
- The `message_label` parameter is either a string label returned by the AlarmProcessor function or `None`. This label indicates the type of message that should be constructed (e.g., "reminder", "alert", etc.).
- The`logger` parameter is a logging object that can be used to log debug messages or other information during the construction of the message.

Parameters in this function should be treated as read-only. One such function could look like this:
```python
def decanter_activation_msg_builder(alarm: Alarm, event: Event, plant: Plant, message_label: Union[str, bool]="activation", logger: logging.Logger) -> str:
	"""
	builds the message for an activation event
	"""
	decanter_id = event['decanter_id']
	event_time = event['timestamp']
	
	plant_name = plant['plant_name_proper']
	
	return f"Decanter {decanter_id} at {plant_name} detected broken at {event_time}"
```

Once defined, this function must be registered with the system as shown in the [usage](README#Usage) section.

---
## System architechture
The AlarmSystem is composed of four main components: the orchestrator, a connector, a processor, and a notifier. The orchestrator component interacts with the connector, processor, and notifier via interfaces. This abstraction enables the system to be extended with updated components or  adapted to different data sources, processing logic, or notification mechanisms.

### Component abstraction
This project was designed from the ground up with modularity in mind. As such, the following interfaces are made public in the `alarm_system.interfaces` module:

```python
from .src.core.interfaces.connector import IConnector
from .src.core.interfaces.notifier import INotifier
from .src.core.interfaces.processor import IProcessor
```
Each interface is defined as follows:

connector.py
```python
class IConnector(ABC):
	"""
	This interface manages connecting to a data source for reading and writing event data
	"""
	logger: logging.Logger
	
	@abstractmethod
	def load_system_data(self) -> Tuple[List[Alarm], List[Plant], List[PlantContacts], List[Event]]:
		"""
		loads alarm, plant, contact and event data for the alarm system
		"""
	
	@abstractmethod
	def update_system_alarms(self, alarms: List[Alarm]) -> bool:
		"""
		update list of alarms for future reuse
		:param alarms: the alarms to update in a remote database
		:returns: bool whether the update was successful or not
		"""
```

notifier.py
```python
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
```

processor.py
```python
class IProcessor(ABC):
	"""
	This interface manages processing the bulk of the data
	"""
	logger: logging.Logger
	
	@abstractmethod
	def process_event(self, alarm: Alarm, plant: Plant, event: Event) -> Union[str, None]:
		"""
		process an event and immediately return the result
		"""
```

An alarm system is then assembled as follows:
```python
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
		...
```

### Building your own Alarm System
You can replace the default implementations of the connector, processor, and notifier with your own custom classes as long as they adhere to the corresponding interfaces.

Here's an example of how you could implement a custom connector: 
```python
from alarm_system.interfaces import IConnector
from alarm_system.types import Alarm, Plant, PlantContacts, Event
class MyCustomConnector(IConnector):
	def __init__(self, config) -> None # Initialize your custom connector with the provided config
		...
	
	def load_system_data(self) -> Tuple[List[Alarm], List[Plant], List[PlantContacts], List[Event]]: # Implement your logic to load the required data from your custom data source
		...
	
	def update_system_alarms(self, alarms: List[Alarm]) -> bool: # Implement your logic to update the list of alarms in your custom data source # Return True if the update was successful, False otherwise
		...
```
You then create the class manually as follows:
```python
from alarm_system import Orchestrator, EventNotifier, EventProcessor

config = ...

connector = MyCustomConnector(config)

processor = EventProcessor()

notifier_config = {	"sender_email": sender_email,
	"sender_password": sender_password,
	"sender_sms": sender_sms,
	"token_sms": token_sms,
	"pemfile_sms": pemfile_sms
}
notifier = EventNotifier(notifier_config, logger)

orchestrator = Orchestrator(connector, processor, notifier, self.logger)
```
The process is the same for any combination of new components.

The default AlarmSystem class is actually a wrapper over a concrete orchestrator build:

\_\_init\_\_.py
```python
import logging
...

# These classes implement their respective interfaces and thus can be used to create an alarm system
from .src.processor.event_processor import EventProcessor
from .src.notifier.event_notifier import EventNotifier
from .src.connector.mongodb_connector import MongoDBConnector

# The core of the alarm system
from .src.core.orchestrator import Orchestrator

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
		
		# Create a concrete system from the provided interface implementations
		self.orchestrator = Orchestrator(connector, processor, notifier, self.logger)
		
		self.logger.info(f"AlarmSystem created")
	...
```
You can create your own components. As long as you adhere to the interfaces, you will be able to create an alarm system.