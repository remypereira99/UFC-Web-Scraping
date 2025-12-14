from dataclasses import dataclass
from typing import Optional


@dataclass
class FightStats:
    total_strikes_landed: int
    total_strikes_attempted: int
    significant_strikes_landed: int
    significant_strikes_attempted: int
    knockdowns: int
    takedowns_landed: int
    takedowns_attempted: int
    control_time_minutes: int
    control_time_seconds: int
    submissions_attempted: int
    reversals: int


@dataclass
class Fight:
    weight_class: str
    num_rounds: int
    finish_method: str
    finish_submethod: str
    finish_round: int
    finish_time: str
    finish_time_minute: int
    finish_time_second: int
    referee: str


@dataclass
class Fighter:
    full_name: str
    first_name: str
    last_name: str
    nickname: Optional[str]
    height_ft: int
    height_in: int
    height_cm: int
    weight_lbs: int
    reach_in: int
    reach_cm: int
    stance: str
    dob: str


@dataclass
class FighterRecord:
    wins: int
    losses: int
    draws: int
    no_contests: int


@dataclass
class Event:
    event_id: str
    url: str
    name: str
    date: str
    location: str
    city: str
    state: str
    country: str
    fights: str
