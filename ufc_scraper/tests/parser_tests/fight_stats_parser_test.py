from freezegun import freeze_time
import pytest

from entities import FightStats
from ufc_scraper.ufc_scraper.parsers.fight_stat_parser import FightStatParser
from tests import FIGHT_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file
from utils import get_uuid_string


@pytest.fixture
def fight_stat_parser_valid() -> FightStatParser:
    fight_stat_response = load_html_response_from_file(FIGHT_RESPONSE_VALID_PATH)

    return FightStatParser(fight_stat_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_fight_stat_parse_response_valid(
    fight_stat_parser_valid: FightStatParser,
) -> None:
    parsed_response = list(fight_stat_parser_valid.parse_response())

    fight_id = get_uuid_string("http://ufcstats.com/fight_response_valid")
    fighter_1_id = get_uuid_string(
        "http://ufcstats.com/fighter-details/d661ce4da776fc20"
    )
    fighter_1_fight_stat_id = get_uuid_string(fight_id + fighter_1_id)
    fighter_2_id = get_uuid_string(
        "http://ufcstats.com/fighter-details/aa72b0f831d0bfe5"
    )
    fighter_2_fight_stat_id = get_uuid_string(fight_id + fighter_2_id)

    expected_response_fighter_1 = FightStats(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_id=fighter_1_fight_stat_id,
        fight_id=fight_id,
        fighter_id=fighter_1_id,
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
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_id=fighter_2_fight_stat_id,
        fight_id=fight_id,
        fighter_id=fighter_2_id,
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
