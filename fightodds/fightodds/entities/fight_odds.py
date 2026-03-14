"""Defines dataclass for parsed FightOdds output."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FightOdds:
    """Dataclass for UFC fight betting odds per sportsbook from fightodds.io."""

    scraped_at: str
    fight_odds_id: str
    fight_slug: str
    fighter_1_id: str
    fighter_1_first_name: str
    fighter_1_last_name: str
    fighter_2_id: str
    fighter_2_first_name: str
    fighter_2_last_name: str
    best_odds_1: Optional[int]
    best_odds_2: Optional[int]
    sportsbook_short_name: str
    sportsbook_slug: str
    outcome_1_odds: Optional[int]
    outcome_1_odds_open: Optional[int]
    outcome_1_odds_best: Optional[int]
    outcome_1_odds_worst: Optional[int]
    outcome_1_odds_prev: Optional[int]
    outcome_2_odds: Optional[int]
    outcome_2_odds_open: Optional[int]
    outcome_2_odds_best: Optional[int]
    outcome_2_odds_worst: Optional[int]
    outcome_2_odds_prev: Optional[int]
