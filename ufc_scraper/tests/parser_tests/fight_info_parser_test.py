from freezegun import freeze_time
import pytest

from entities import Fight
from parsers import FightInfoParser
from tests import FIGHT_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file


@pytest.fixture
def fight_info_parser_valid() -> FightInfoParser:
    fight_response = load_html_response_from_file(FIGHT_RESPONSE_VALID_PATH)

    return FightInfoParser(fight_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_fight_info_parse_response_valid(
    fight_info_parser_valid: FightInfoParser,
) -> None:
    parsed_response = fight_info_parser_valid.parse_response()

    expected_response = Fight(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_id="6c8c2ab9-07f2-511f-ac1f-5037fbc2bf42",
        url="http://www.ufcstats.com/fight_response_valid",
        fighter_1_id="957ba518-e9ac-576b-92ef-8d60d89e73a1",
        fighter_2_id="1fa816e9-e0c1-56b8-a267-4daf7b1e07ab",
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
