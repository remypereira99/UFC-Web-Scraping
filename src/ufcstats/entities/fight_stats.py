"""Defines dataclass for parsed FightStats output."""

from dataclasses import dataclass


@dataclass
class FightStats:
    """Dataclass for UFC fight stats per fighter."""

    scraped_at: str
    fight_stat_id: str
    fight_id: str
    fighter_id: str
    url: str
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
