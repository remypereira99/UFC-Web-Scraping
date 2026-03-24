"""Defines dataclass for parsed Fight output."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Fight:
    """Dataclass for general UFC fight attributes."""

    scraped_at: str
    fight_id: str
    event_id: str
    url: str
    fighter_1_id: str
    fighter_2_id: str
    fighter_1_outcome: str
    fighter_2_outcome: str
    bout_type: str
    weight_class: Optional[str]
    num_rounds: int
    finish_method: str
    primary_finish_method: str
    secondary_finish_method: str
    finish_round: int
    finish_time_minute: int
    finish_time_second: int
    referee: str
    judge_1: str
    judge_2: str
    judge_3: str
