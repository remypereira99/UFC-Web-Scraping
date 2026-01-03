from freezegun import freeze_time
import pytest

from entities import Fight
from ufc_scraper.parsers.fight_info_parser import FightInfoParser
from tests import FIGHT_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file
from utils import get_uuid_string


@pytest.fixture
def fight_info_parser_valid() -> FightInfoParser:
    fight_response = load_html_response_from_file(FIGHT_RESPONSE_VALID_PATH)

    return FightInfoParser(fight_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_fight_info_parse_response_valid(
    fight_info_parser_valid: FightInfoParser,
) -> None:
    parsed_response = fight_info_parser_valid.parse_response()

    fight_id = get_uuid_string("http://ufcstats.com/fight_response_valid")
    event_id = get_uuid_string("http://ufcstats.com/event-details/e955046551f8c7dd")
    fighter_1_id = get_uuid_string(
        "http://ufcstats.com/fighter-details/d661ce4da776fc20"
    )
    fighter_2_id = get_uuid_string(
        "http://ufcstats.com/fighter-details/aa72b0f831d0bfe5"
    )

    expected_response = Fight(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_id=fight_id,
        event_id=event_id,
        url="http://www.ufcstats.com/fight_response_valid",
        fighter_1_id=fighter_1_id,
        fighter_2_id=fighter_2_id,
        fighter_1_outcome="W",
        fighter_2_outcome="L",
        weight_class="bantamweight",
        num_rounds=5,
        finish_method="Decision - Unanimous",
        primary_finish_method="decision",
        secondary_finish_method="unanimous",
        finish_round=5,
        finish_time_minute=5,
        finish_time_second=0,
        referee="Mike Beltran",
        judge_1="Sal D'amato",
        judge_2="David Lethaby",
        judge_3="Clemens Werner",
    )

    assert parsed_response == expected_response
