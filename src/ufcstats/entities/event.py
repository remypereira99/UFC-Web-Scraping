"""Defines dataclass for parsed Event output."""

from dataclasses import dataclass


@dataclass
class Event:
    """Dataclass for general UFC event attributes."""

    scraped_at: str
    event_id: str
    url: str
    name: str
    date: str
    date_formatted: str
    city: str
    state: str
    country: str
    fights: str
