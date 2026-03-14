"""Parser for fightodds.io GraphQL JSON fighter responses."""

from datetime import datetime, timezone
from typing import Any, Iterator

from fightodds.entities.fighter import Fighter


class FighterParser:
    """Parses GraphQL JSON responses from fightodds.io fighter pages.

    Parses key attributes of a UFC fighter and yields a Fighter dataclass.

    Args:
        response: The Scrapy HTTP response containing a JSON body.

    Attributes:
        _fighter (dict): The fighter node from the GQL response.

    """

    def __init__(self, response: Any) -> None:
        self._fighter = response.json()["data"]["fighter"]

    def parse_response(self) -> Iterator[Fighter]:
        """Parse the JSON response to get fighter stats.

        Returns:
            Iterator[Fighter]: Yields one Fighter dataclass.

        """
        grappling_style_names = [
            edge["node"]["name"] for edge in self._fighter["grapplingStyle"]["edges"]
        ]
        grappling_style = ", ".join(grappling_style_names) or None

        yield Fighter(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            fighter_id=self._fighter["id"],
            fighter_slug=self._fighter["slug"],
            first_name=self._fighter["firstName"],
            last_name=self._fighter["lastName"],
            birth_date=self._fighter["birthDate"],
            fighting_style=self._fighter["fightingStyle"],
            nationality=self._fighter["nationality"],
            grappling_style=grappling_style,
            height_cm=self._fighter["height"],
            reach_cm=self._fighter["reach"],
            stance=self._fighter["stance"],
            leg_reach_cm=self._fighter["legReach"],
        )
