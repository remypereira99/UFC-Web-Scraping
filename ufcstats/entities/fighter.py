"""Defines dataclass for parsed Fighter output."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Fighter:
    """Dataclass for general UFC fighter attributes."""

    scraped_at: str
    fighter_id: str
    url: str
    full_name: str
    first_name: str
    last_names: str
    nickname: Optional[str]
    height_ft: Optional[int]
    height_in: Optional[int]
    height_cm: Optional[float]
    weight_lbs: Optional[int]
    reach_in: Optional[int]
    reach_cm: Optional[int]
    stance: str
    dob: Optional[str]
    dob_formatted: Optional[str]
    record: str
    wins: int
    losses: int
    draws: int
    no_contests: int
    fight_ids: Optional[str]
