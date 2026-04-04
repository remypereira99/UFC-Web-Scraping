from freezegun import freeze_time
import pytest

from entities import Fighter
from ufc_scraper.parsers.fighter_info_parser import FighterInfoParser
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
    fight_urls = [
        "http://www.ufcstats.com/fight-details/6b8be0ee3e569ad2",
        "http://www.ufcstats.com/fight-details/b8bf186f884678ea",
        "http://www.ufcstats.com/fight-details/eba46dbf9cdd83c0",
        "http://www.ufcstats.com/fight-details/01432891260084a4",
        "http://www.ufcstats.com/fight-details/4ec5d9bd1442e6c1",
        "http://www.ufcstats.com/fight-details/b8ca1acdf3dc2f58",
        "http://www.ufcstats.com/fight-details/ca8f73d038c4d6e7",
        "http://www.ufcstats.com/fight-details/f67aa0b16e16a9ea",
        "http://www.ufcstats.com/fight-details/51108eabae8391ca",
        "http://www.ufcstats.com/fight-details/11f715fa5e825e51",
        "http://www.ufcstats.com/fight-details/2556b7520536ce1d",
        "http://www.ufcstats.com/fight-details/5a09fd7cb3db9705",
        "http://www.ufcstats.com/fight-details/06cd9812e2b9b747",
        "http://www.ufcstats.com/fight-details/0459297e86a14981",
        "http://www.ufcstats.com/fight-details/6d04fbef6b8e4551",
        "http://www.ufcstats.com/fight-details/b65d0243d397802c",
        "http://www.ufcstats.com/fight-details/766dc3c5592b4d0d",
        "http://www.ufcstats.com/fight-details/7ec24848cac6c5a1",
        "http://www.ufcstats.com/fight-details/13c4251fb451f440",
        "http://www.ufcstats.com/fight-details/1f65f03f1225e061",
        "http://www.ufcstats.com/fight-details/ab0d6346b7938a7f",
        "http://www.ufcstats.com/fight-details/f18ea0d8b472dc1e",
        "http://www.ufcstats.com/fight-details/3333fdbe86a763fb",
        "http://www.ufcstats.com/fight-details/d6b3c56a4cf14c1a",
    ]
    fight_id_list = [get_uuid_string(url) for url in fight_urls]
    fight_ids = ", ".join(fight_id_list)

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
        fight_ids=fight_ids,
    )

    assert parsed_response == expected_response
