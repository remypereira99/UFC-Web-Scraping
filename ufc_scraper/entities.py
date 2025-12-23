from dataclasses import dataclass
from typing import Optional


@dataclass
class FightStats:
    fight_stat_id: str
    fight_id: str
    fighter_id: str
    total_strikes_landed: int
    total_strikes_attempted: int
    significant_strikes_landed: int
    significant_strikes_attempted: int
    significant_strikes_landed_head: int
    significant_strikes_attempted_head: int
    significant_strikes_landed_body: int
    significant_strikes_attempted_body: int
    significant_strikes_landed_leg: int
    significant_strikes_attempted_leg: int
    significant_strikes_landed_distance: int
    significant_strikes_attempted_distance: int
    significant_strikes_landed_clinch: int
    significant_strikes_attempted_clinch: int
    significant_strikes_landed_ground: int
    significant_strikes_attempted_ground: int
    knockdowns: int
    takedowns_landed: int
    takedowns_attempted: int
    control_time_minutes: int
    control_time_seconds: int
    submissions_attempted: int
    reversals: int


@dataclass
class Fight:
    fight_id: str
    url: str
    fighter_1_id: str
    fighter_2_id: str
    weight_class: str
    num_rounds: int
    finish_method: str
    finish_submethod: str
    finish_round: int
    finish_time_minute: int
    finish_time_second: int
    referee: str
    judge_1_id: str
    judge_2_id: str
    judge_3_id: str


@dataclass
class Fighter:
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
    dob: str
    record: str
    wins: int
    losses: int
    draws: int
    no_contests: int
    opponents: str


@dataclass
class Event:
    event_id: str
    url: str
    name: str
    date: str
    date_formatted: str
    city: str
    state: str
    country: str
    fights: str
