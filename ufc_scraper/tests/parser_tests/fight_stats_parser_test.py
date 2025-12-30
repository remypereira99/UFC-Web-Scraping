from tests.utils import load_html_response_from_file

import pytest

from tests import FIGHT_RESPONSE_VALID_PATH
from entities import FightStats
from parsers import FightStatParser


@pytest.fixture
def fight_stat_parser_valid() -> FightStatParser:
    fight_stat_response = load_html_response_from_file(FIGHT_RESPONSE_VALID_PATH)

    return FightStatParser(fight_stat_response)


def test_fight_stat_parse_response_valid(
    fight_stat_parser_valid: FightStatParser,
) -> None:
    parsed_response = list(fight_stat_parser_valid.parse_response())

    expected_response_fighter_1 = FightStats(
        fight_stat_id="d0e81594-355c-59a2-a7c8-5b4790107ce8",
        fight_id="6c8c2ab9-07f2-511f-ac1f-5037fbc2bf42",
        fighter_id="957ba518-e9ac-576b-92ef-8d60d89e73a1",
        url="http://www.ufcstats.com/fight_response_valid",
        total_strikes_landed=190,
        total_strikes_attempted=263,
        significant_strikes_landed=121,
        significant_strikes_attempted=193,
        significant_strikes_landed_head=78,
        significant_strikes_attempted_head=142,
        significant_strikes_landed_body=18,
        significant_strikes_attempted_body=21,
        significant_strikes_landed_leg=25,
        significant_strikes_attempted_leg=30,
        significant_strikes_landed_distance=103,
        significant_strikes_attempted_distance=172,
        significant_strikes_landed_clinch=13,
        significant_strikes_attempted_clinch=15,
        significant_strikes_landed_ground=5,
        significant_strikes_attempted_ground=6,
        knockdowns=0,
        takedowns_landed=1,
        takedowns_attempted=4,
        control_time_minutes=3,
        control_time_seconds=21,
        submissions_attempted=0,
        reversals=1,
    )

    expected_response_fighter_2 = FightStats(
        fight_stat_id="8a65ff90-c455-5d2f-9666-262032f8bfe4",
        fight_id="6c8c2ab9-07f2-511f-ac1f-5037fbc2bf42",
        fighter_id="1fa816e9-e0c1-56b8-a267-4daf7b1e07ab",
        url="http://www.ufcstats.com/fight_response_valid",
        total_strikes_landed=53,
        total_strikes_attempted=119,
        significant_strikes_landed=53,
        significant_strikes_attempted=119,
        significant_strikes_landed_head=23,
        significant_strikes_attempted_head=75,
        significant_strikes_landed_body=24,
        significant_strikes_attempted_body=36,
        significant_strikes_landed_leg=6,
        significant_strikes_attempted_leg=8,
        significant_strikes_landed_distance=49,
        significant_strikes_attempted_distance=112,
        significant_strikes_landed_clinch=4,
        significant_strikes_attempted_clinch=7,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=2,
        takedowns_attempted=8,
        control_time_minutes=3,
        control_time_seconds=0,
        submissions_attempted=0,
        reversals=0,
    )

    assert parsed_response[0] == expected_response_fighter_1
    assert parsed_response[1] == expected_response_fighter_2
