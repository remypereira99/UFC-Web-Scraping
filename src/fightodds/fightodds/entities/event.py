"""Defines dataclass for parsed Event output."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """Dataclass for UFC event overview attributes from fightodds.io."""

    scraped_at: str
    event_pk: int
    event_id: Optional[str]
    event_slug: str
    event_name: str
    event_date: str
    event_city: Optional[str]
    event_state: Optional[str]
    event_country: Optional[str]
    fight_slugs: str
    fight_ids: str
