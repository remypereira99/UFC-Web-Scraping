from freezegun import freeze_time
import pytest

from entities import Fighter
from parsers import FighterInfoParser
from tests import FIGHTER_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file
from utils import get_uuid_string


@pytest.fixture
def fighter_info_parser_valid() -> FighterInfoParser:
    fighter_response = load_html_response_from_file(FIGHTER_RESPONSE_VALID_PATH)

    return FighterInfoParser(fighter_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_fighter_info_parse_response_valid(
    fighter_info_parser_valid: FighterInfoParser,
) -> None:
    parsed_response = fighter_info_parser_valid.parse_response()

    fighter_id = get_uuid_string("http://ufcstats.com/fighter_response_valid")
    opponent_urls = [
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/d549cefc7c54ab78",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/767755fd74662dbf",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/b07aed698fba8624",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/2e5c2aa8e4ab9d82",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/0d7b51c9d2649a6e",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/7acbb0972e75281a",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/1338e2c7480bdf9e",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/8c0580d4fff106c1",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/13a0275fa13c4d26",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/9ce6d5a03af801b7",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/1338e2c7480bdf9e",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/f77c68bb4be8516d",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/f77c68bb4be8516d",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/7a703c565ccaa18f",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/b1a3e0aca758b322",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/0dba4df5f34d5ff0",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/65578a75fa7900e3",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/0c6d9ea8306c029e",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/92b62174c175ce19",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/b7ad576b8ae115e6",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/4a28cb716c19157a",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/523fa774700d7d3f",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/2e25c1d983c26311",
        "http://ufcstats.com/fighter-details/e1147d3d2dabe1ce",
        "http://ufcstats.com/fighter-details/34e552520a934063",
    ]
    opponent_id_list = [get_uuid_string(url) for url in opponent_urls]
    opponent_ids = ", ".join(opponent_id_list)

    expected_response = Fighter(
        scraped_at="2000-01-01 00:00:00 UTC",
        fighter_id=fighter_id,
        url="http://www.ufcstats.com/fighter_response_valid",
        full_name="Robert Whittaker",
        first_name="Robert",
        last_names="Whittaker",
        nickname="The Reaper",
        height_ft=6,
        height_in=0,
        height_cm=182.88,
        weight_lbs=185,
        reach_in=73,
        reach_cm=185,
        stance="Orthodox",
        dob="Dec 20, 1990",
        dob_formatted="1990-12-20",
        record="27-9-0",
        wins=27,
        losses=9,
        draws=0,
        no_contests=0,
        opponents=opponent_ids,
    )

    assert parsed_response == expected_response
