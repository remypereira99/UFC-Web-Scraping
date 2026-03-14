"""Defines dataclass for parsed Fighter output."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Fighter:
    """Dataclass for UFC fighter stats from fightodds.io."""

    scraped_at: str
    fighter_id: str
    fighter_slug: str
    first_name: str
    last_name: str
    birth_date: Optional[str]
    fighting_style: Optional[str]
    nationality: Optional[str]
    grappling_style: Optional[str]
    height: Optional[float]
    reach: Optional[float]
    stance: Optional[str]
    leg_reach: Optional[float]
