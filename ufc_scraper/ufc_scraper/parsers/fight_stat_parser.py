"""HTML parsers for UFCStats pages.

This module contains Scrapy-based parsers for UFC events, fights,
fighters, and fight statistics (total and by-round).
"""

from datetime import datetime, timezone
from typing import Any, Iterator

from scrapy.http import Response

from . import (
    TOTALS_STATS_EXPECTED_HEADERS,
    SIGNIFICANT_STRIKES_EXPECTED_HEADERS,
)
from base_parser import Parser
from entities import FightStats, FightStatsByRound
from utils import (
    clean_string,
    get_uuid_string,
    get_strikes_landed_attempted,
)


class FightStatParser(Parser):
    """Parses HTTP responses of ufcstats.com fight pages.

    Parses fight statistics from UFC fights and yields a FightStats dataclass
    for each fighter.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.
        _css_queries (Dict[str, str]): Mapping of semantic query names to
            CSS selectors used to extract fight metadata from the response.

    """

    def __init__(self, response: Response):
        super().__init__(response)
        self._fight_id = self._id
        self._get_fighter_ids()

    def _get_fighter_ids(self) -> None:
        fighter_urls = tuple(
            self._safe_css_get_all(self._css_queries.fighter_urls_query)
        )
        fighter_1_url, fighter_2_url = fighter_urls
        self._fighter_1_id = get_uuid_string(fighter_1_url)
        self._fighter_2_id = get_uuid_string(fighter_2_url)

    def _get_fight_stat_headers(self) -> None:
        headers = self._safe_css_get_all(self._css_queries.fight_stat_headers_query)
        headers_clean = [clean_string(header) for header in headers]

        round_headers = self._safe_css_get_all(self._css_queries.round_headers_query)
        round_headers_clean = [
            clean_string(round_header) for round_header in round_headers
        ]
        # Divide by two as the number of rounds is duplicated for stats and significant strikes
        self._num_rounds = int(len(round_headers_clean) / 2)

        totals_headers_clean = headers_clean[0:10]
        totals_headers_clean.remove("Fighter")
        assert totals_headers_clean == TOTALS_STATS_EXPECTED_HEADERS, (
            f"Totals headers {totals_headers_clean} for url {self._url}",
            f"do not match expected headers: {TOTALS_STATS_EXPECTED_HEADERS}",
        )
        totals_by_round_headers = [
            f"{header}_round_{round}"
            for round in range(1, self._num_rounds + 1)
            for header in totals_headers_clean
        ]

        sig_strikes_headers_clean = headers_clean[10:]
        sig_strikes_headers_clean.remove("Fighter")
        assert sig_strikes_headers_clean == SIGNIFICANT_STRIKES_EXPECTED_HEADERS, (
            f"Totals headers {sig_strikes_headers_clean} for url {self._url}",
            f"do not match expected headers: {SIGNIFICANT_STRIKES_EXPECTED_HEADERS}",
        )
        sig_strikes_by_round_headers = [
            f"{header}_round_{round}"
            for round in range(1, self._num_rounds + 1)
            for header in sig_strikes_headers_clean
        ]

        self._all_stat_headers = (
            totals_headers_clean
            + totals_by_round_headers
            + sig_strikes_headers_clean
            + sig_strikes_by_round_headers
        )

    def _get_fight_stat_values(self) -> None:
        values = self._safe_css_get_all(self._css_queries.fight_stat_values_query)
        values_clean = [
            clean_string(value) for value in values if clean_string(value) != ""
        ]

        self._fighter_1_stat_values = values_clean[0::2]
        self._fighter_2_stat_values = values_clean[1::2]

    def _get_fight_stat_dicts(self) -> None:
        self._get_fight_stat_headers()
        self._get_fight_stat_values()

        num_fighter_1_values = len(self._fighter_1_stat_values)
        num_fighter_2_values = len(self._fighter_2_stat_values)
        num_headers = len(self._all_stat_headers)
        assert num_fighter_1_values == num_headers, (
            f"Number of stat values {num_fighter_1_values} does not match number of",
            f"headers {num_headers} for fighter_1: {self._fighter_1_id}",
        )
        assert num_fighter_2_values == num_headers, (
            f"Number of stat values {num_fighter_2_values} does not match number of",
            f"headers {num_headers} for fighter_1: {self._fighter_2_id}",
        )

        fighter_1_stats_dict = dict(
            zip(self._all_stat_headers, self._fighter_1_stat_values)
        )
        fighter_2_stats_dict = dict(
            zip(self._all_stat_headers, self._fighter_2_stat_values)
        )
        self._fighter_stats_dicts = {
            self._fighter_1_id: fighter_1_stats_dict,
            self._fighter_2_id: fighter_2_stats_dict,
        }

    def _get_fight_stats(self, fighter_id: str) -> FightStats:
        self._get_fight_stat_dicts()
        fighter_stat_dict = self._fighter_stats_dicts[fighter_id]

        fight_stat_id = get_uuid_string(self._fight_id + fighter_id)
        (total_strikes_landed, total_strikes_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict["Total str."]
        )
        (significant_strikes_landed, significant_strikes_attempted) = (
            get_strikes_landed_attempted(fighter_stat_dict["Sig. str.)"])
        )
        (significant_strikes_landed_head, significant_strikes_attempted_head) = (
            get_strikes_landed_attempted(fighter_stat_dict["Head)"])
        )
        (significant_strikes_landed_body, significant_strikes_attempted_body) = (
            get_strikes_landed_attempted(fighter_stat_dict["Body)"])
        )
        (significant_strikes_landed_leg, significant_strikes_attempted_leg) = (
            get_strikes_landed_attempted(fighter_stat_dict["Leg)"])
        )
        (
            significant_strikes_landed_distance,
            significant_strikes_attempted_distance,
        ) = get_strikes_landed_attempted(fighter_stat_dict["Distance)"])
        (significant_strikes_landed_clinch, significant_strikes_attempted_clinch) = (
            get_strikes_landed_attempted(fighter_stat_dict["Clinch)"])
        )
        (significant_strikes_landed_ground, significant_strikes_attempted_ground) = (
            get_strikes_landed_attempted(fighter_stat_dict["Ground)"])
        )
        knockdowns = int(fighter_stat_dict["KD)"])
        (takedowns_landed, takedowns_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict["Td"]
        )
        control_time_raw = clean_string(fighter_stat_dict["Ctrl)"])
        (control_time_minutes_string, control_time_seconds_string) = (
            control_time_raw.split(":")
        )
        control_time_minutes = int(control_time_minutes_string)
        control_time_seconds = int(control_time_seconds_string)
        submissions_attempted = int(fighter_stat_dict["Sub. att)"])
        reversals = int(fighter_stat_dict["Rev.)"])

        return FightStats(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            fight_stat_id=fight_stat_id,
            fight_id=self._fight_id,
            fighter_id=fighter_id,
            url=self._url,
            total_strikes_landed=total_strikes_landed,
            total_strikes_attempted=total_strikes_attempted,
            significant_strikes_landed=significant_strikes_landed,
            significant_strikes_attempted=significant_strikes_attempted,
            significant_strikes_landed_head=significant_strikes_landed_head,
            significant_strikes_attempted_head=significant_strikes_attempted_head,
            significant_strikes_landed_body=significant_strikes_landed_body,
            significant_strikes_attempted_body=significant_strikes_attempted_body,
            significant_strikes_landed_leg=significant_strikes_landed_leg,
            significant_strikes_attempted_leg=significant_strikes_attempted_leg,
            significant_strikes_landed_distance=significant_strikes_landed_distance,
            significant_strikes_attempted_distance=significant_strikes_attempted_distance,
            significant_strikes_landed_clinch=significant_strikes_landed_clinch,
            significant_strikes_attempted_clinch=significant_strikes_attempted_clinch,
            significant_strikes_landed_ground=significant_strikes_landed_ground,
            significant_strikes_attempted_ground=significant_strikes_attempted_ground,
            knockdowns=knockdowns,
            takedowns_landed=takedowns_landed,
            takedowns_attempted=takedowns_attempted,
            control_time_minutes=control_time_minutes,
            control_time_seconds=control_time_seconds,
            submissions_attempted=submissions_attempted,
            reversals=reversals,
        )

    def parse_response(self) -> Iterator[Any]:
        """Parse the HTML response to get key fight stats.

        Args:
            response (Response): The response object to query.

        Returns:
            Iterator[FightStats]: Dataclass containing all key fight stats attributes.
                Yields one FightStats object per fighter.

        """
        fighter_1_stats = self._get_fight_stats(self._fighter_1_id)
        fighter_2_stats = self._get_fight_stats(self._fighter_2_id)

        yield fighter_1_stats
        yield fighter_2_stats


class FightStatByRoundParser(FightStatParser):
    """Parses HTTP responses of ufcstats.com fight pages.

    Parses fight statistics from each round of UFC fights and yields a FightStatsByRound
    dataclass per fighter per round.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.

    """

    def __init__(self, response: Response):
        super().__init__(response)

    def _get_fight_stats_by_round(
        self, fighter_id: str, round: int
    ) -> FightStatsByRound:
        fighter_stat_dict = self._fighter_stats_dicts[fighter_id]
        fight_stat_by_round_id = get_uuid_string(
            self._fight_id + fighter_id + str(round)
        )

        (total_strikes_landed, total_strikes_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict[f"Total str._round_{round}"]
        )
        (significant_strikes_landed, significant_strikes_attempted) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Sig. str._round_{round})"])
        )
        (significant_strikes_landed_head, significant_strikes_attempted_head) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Head_round_{round})"])
        )
        (significant_strikes_landed_body, significant_strikes_attempted_body) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Body_round_{round})"])
        )
        (significant_strikes_landed_leg, significant_strikes_attempted_leg) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Leg_round_{round})"])
        )
        (
            significant_strikes_landed_distance,
            significant_strikes_attempted_distance,
        ) = get_strikes_landed_attempted(fighter_stat_dict[f"Distance_round_{round})"])
        (significant_strikes_landed_clinch, significant_strikes_attempted_clinch) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Clinch_round_{round})"])
        )
        (significant_strikes_landed_ground, significant_strikes_attempted_ground) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Ground_round_{round})"])
        )
        knockdowns = int(fighter_stat_dict[f"KD_round_{round})"])
        (takedowns_landed, takedowns_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict[f"Td_round_{round}"]
        )
        control_time_raw = clean_string(fighter_stat_dict[f"Ctrl_round_{round})"])
        (control_time_minutes_string, control_time_seconds_string) = (
            control_time_raw.split(":")
        )
        control_time_minutes = int(control_time_minutes_string)
        control_time_seconds = int(control_time_seconds_string)
        submissions_attempted = int(fighter_stat_dict[f"Sub. att_round_{round})"])
        reversals = int(fighter_stat_dict[f"Rev._round_{round})"])

        return FightStatsByRound(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            fight_stat_by_round_id=fight_stat_by_round_id,
            fight_id=self._fight_id,
            fighter_id=fighter_id,
            round=round,
            total_strikes_landed=total_strikes_landed,
            total_strikes_attempted=total_strikes_attempted,
            significant_strikes_landed=significant_strikes_landed,
            significant_strikes_attempted=significant_strikes_attempted,
            significant_strikes_landed_head=significant_strikes_landed_head,
            significant_strikes_attempted_head=significant_strikes_attempted_head,
            significant_strikes_landed_body=significant_strikes_landed_body,
            significant_strikes_attempted_body=significant_strikes_attempted_body,
            significant_strikes_landed_leg=significant_strikes_landed_leg,
            significant_strikes_attempted_leg=significant_strikes_attempted_leg,
            significant_strikes_landed_distance=significant_strikes_landed_distance,
            significant_strikes_attempted_distance=significant_strikes_attempted_distance,
            significant_strikes_landed_clinch=significant_strikes_landed_clinch,
            significant_strikes_attempted_clinch=significant_strikes_attempted_clinch,
            significant_strikes_landed_ground=significant_strikes_landed_ground,
            significant_strikes_attempted_ground=significant_strikes_attempted_ground,
            knockdowns=knockdowns,
            takedowns_landed=takedowns_landed,
            takedowns_attempted=takedowns_attempted,
            control_time_minutes=control_time_minutes,
            control_time_seconds=control_time_seconds,
            submissions_attempted=submissions_attempted,
            reversals=reversals,
        )

    def parse_response(self) -> Iterator[Any]:
        """Parse the HTML response to get key fight stats per round.

        Args:
            response (Response): The response object to query.

        Returns:
            Iterator[FightStatsByRound]: Dataclass containing all key fight stats attributes.
                Yields one FightStatsByRound object per fighter per round.

        """
        self._get_fight_stat_dicts()

        for fighter_id in self._fighter_1_id, self._fighter_2_id:
            for round in range(1, self._num_rounds + 1):
                yield self._get_fight_stats_by_round(fighter_id=fighter_id, round=round)
