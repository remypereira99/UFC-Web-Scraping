"""Parser for fightodds.io GraphQL JSON fighter responses."""

from datetime import datetime, timezone
from typing import Any, Iterator

from fightodds.entities.fighter import Fighter
from utils import clean_string


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

    def _get_fighter_names(self) -> None:
        first_name_clean = clean_string(self._fighter["firstName"])
        last_names_clean = clean_string(self._fighter["lastName"])
        full_name = " ".join([first_name_clean, last_names_clean])
        self._first_name_clean = first_name_clean
        self._last_names_clean = last_names_clean
        self._full_name = full_name

    def _get_fighter_dob(self) -> None:
        try:
            clean_string(self._fighter["birthDate"])
        except TypeError:
            raise (
                TypeError(
                    f"Invalid date format for {self._fighter['slug']} with {self._fighter['birthDate']}"
                )
            )
        dob_clean = clean_string(self._fighter["birthDate"])
        self._dob_formatted = datetime.strptime(dob_clean, "%Y-%m-%d").strftime(
            "%Y-%m-%d"
        )

    def _get_fighting_style(self) -> None:
        self._fighting_style_clean = (
            clean_string(self._fighter["fightingStyle"])
            if self._fighter["fightingStyle"]
            else None
        )

        grappling_style_names = [
            clean_string(edge["node"]["name"])
            for edge in self._fighter["grapplingStyle"]["edges"]
        ]
        self._grappling_style_clean = ", ".join(grappling_style_names) or None

    def _get_fighter_nationality(self) -> None:
        nationality = self._fighter["nationality"]
        self._nationality_clean = (
            clean_string(nationality)
            if nationality and clean_string(nationality) != "N/A"
            else None
        )

    def _get_fighter_stance(self) -> None:
        stance = self._fighter["stance"]
        self._stance_clean = (
            clean_string(stance) if stance and clean_string(stance) != "N/A" else None
        )

    def _get_fighter_physical_attributes(self) -> None:
        height = self._fighter["height"]
        reach = self._fighter["reach"]
        leg_reach = self._fighter["legReach"]

        self._height_clean = float(height) if height and float(height) > 0 else None
        self._reach_clean = float(reach) if reach and float(reach) > 0 else None
        self._leg_reach_clean = (
            float(leg_reach) if leg_reach and float(leg_reach) > 0 else None
        )

    def parse_response(self) -> Iterator[Fighter]:
        """Parse the JSON response to get fighter stats.

        Returns:
            Iterator[Fighter]: Yields one Fighter dataclass.

        """
        if any(
            [
                self._fighter["id"] is None,
                self._fighter["firstName"] is None or self._fighter["firstName"] == "",
                self._fighter["lastName"] is None or self._fighter["lastName"] == "",
                self._fighter["birthDate"] is None or self._fighter["birthDate"] == "",
            ]
        ):
            return

        self._get_fighter_names()
        self._get_fighter_dob()
        self._get_fighting_style()
        self._get_fighter_nationality()
        self._get_fighter_physical_attributes()
        self._get_fighter_stance()

        yield Fighter(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            fighter_id=self._fighter["id"],
            fighter_slug=self._fighter["slug"],
            full_name=self._full_name,
            first_name=self._first_name_clean,
            last_names=self._last_names_clean,
            dob=self._dob_formatted,
            fighting_style=self._fighting_style_clean,
            nationality=self._nationality_clean,
            grappling_style=self._grappling_style_clean,
            height_cm=self._height_clean,
            reach_cm=self._reach_clean,
            leg_reach_cm=self._leg_reach_clean,
            stance=self._stance_clean,
        )
