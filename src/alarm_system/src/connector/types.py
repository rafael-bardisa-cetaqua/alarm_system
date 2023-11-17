from typing import Dict, Literal

ConnectorConfig = Dict[Literal["url", "db_name", "alarm_collection", "plant_collection", "event_collection", "contacts_collection"], str]
"""
mongodb_loader must get a dictionary with at least these keys to operate correctly
"""