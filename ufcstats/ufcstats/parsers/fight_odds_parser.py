"""Parser for fightodds.io GraphQL JSON responses."""

from datetime import datetime, timezone
from typing import Any, Iterator

from entities import FightOdds
from utils import get_uuid_string


class FightOddsParser:
    """Parses GraphQL JSON responses from fightodds.io fight odds pages.

    Parses key attributes of UFC fight betting odds and yields FightOdds
    dataclasses — one per sportsbook per fight.

    Args:
        response: The Scrapy HTTP response containing a JSON body.

    Attributes:
        _fight_offer_table (dict): The fightOfferTable node from the GQL response.

    """

    def __init__(self, response: Any) -> None:
        self._fight_offer_table = response.json()["data"]["fightOfferTable"]

    def _get_fight_slug(self) -> None:
        self._fight_slug: str = self._fight_offer_table["slug"]

    def _get_fighter_info(self) -> None:
        fighter_1 = self._fight_offer_table["fighter1"]
        self._fighter_1_id: str = fighter_1["id"]
        self._fighter_1_first_name: str = fighter_1["firstName"]
        self._fighter_1_last_name: str = fighter_1["lastName"]

        fighter_2 = self._fight_offer_table["fighter2"]
        self._fighter_2_id: str = fighter_2["id"]
        self._fighter_2_first_name: str = fighter_2["firstName"]
        self._fighter_2_last_name: str = fighter_2["lastName"]

    def _get_best_odds(self) -> None:
        self._best_odds_1: int | None = self._fight_offer_table["bestOdds1"]
        self._best_odds_2: int | None = self._fight_offer_table["bestOdds2"]

    def parse_response(self) -> Iterator[FightOdds]:
        """Parse the JSON response to get fight odds per sportsbook.

        Returns:
            Iterator[FightOdds]: Yields one FightOdds dataclass per sportsbook.

        """
        self._get_fight_slug()
        self._get_fighter_info()
        self._get_best_odds()

        straight_offer_edges = self._fight_offer_table["straightOffers"]["edges"]
        for edge in straight_offer_edges:
            node = edge["node"]
            sportsbook = node["sportsbook"]
            outcome_1 = node["outcome1"]
            outcome_2 = node["outcome2"]

            sportsbook_slug: str = sportsbook["slug"]
            fight_odds_id = get_uuid_string(
                self._fight_slug + sportsbook_slug,
                should_format_href=False,
            )

            yield FightOdds(
                scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                fight_odds_id=fight_odds_id,
                fight_slug=self._fight_slug,
                fighter_1_id=self._fighter_1_id,
                fighter_1_first_name=self._fighter_1_first_name,
                fighter_1_last_name=self._fighter_1_last_name,
                fighter_2_id=self._fighter_2_id,
                fighter_2_first_name=self._fighter_2_first_name,
                fighter_2_last_name=self._fighter_2_last_name,
                best_odds_1=self._best_odds_1,
                best_odds_2=self._best_odds_2,
                sportsbook_short_name=sportsbook["shortName"],
                sportsbook_slug=sportsbook_slug,
                outcome_1_odds=outcome_1["odds"],
                outcome_1_odds_open=outcome_1["oddsOpen"],
                outcome_1_odds_best=outcome_1["oddsBest"],
                outcome_1_odds_worst=outcome_1["oddsWorst"],
                outcome_1_odds_prev=outcome_1["oddsPrev"],
                outcome_2_odds=outcome_2["odds"],
                outcome_2_odds_open=outcome_2["oddsOpen"],
                outcome_2_odds_best=outcome_2["oddsBest"],
                outcome_2_odds_worst=outcome_2["oddsWorst"],
                outcome_2_odds_prev=outcome_2["oddsPrev"],
            )
