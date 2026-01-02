from freezegun import freeze_time
import pytest

from entities import Event
from parsers import EventInfoParser
from tests import EVENT_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file
from utils import get_uuid_string


@pytest.fixture
def event_info_parser_valid() -> EventInfoParser:
    event_response = load_html_response_from_file(EVENT_RESPONSE_VALID_PATH)

    return EventInfoParser(event_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_event_info_parse_response_valid(
    event_info_parser_valid: EventInfoParser,
) -> None:
    parsed_response = event_info_parser_valid.parse_response()

    event_id = get_uuid_string("http://ufcstats.com/event_response_valid")
    fight_urls = [
        "http://ufcstats.com/fight-details/ebf7cea27b83c432",
        "http://ufcstats.com/fight-details/b8bf186f884678ea",
        "http://ufcstats.com/fight-details/b09f54654b0f95f5",
        "http://ufcstats.com/fight-details/cc11a0762f246fa4",
        "http://ufcstats.com/fight-details/108434acbbd75d26",
        "http://ufcstats.com/fight-details/781a2ea50f5ae68f",
        "http://ufcstats.com/fight-details/1d65c141776949d6",
        "http://ufcstats.com/fight-details/919e3c5cc6999cb3",
        "http://ufcstats.com/fight-details/af6eeea1cfe33240",
        "http://ufcstats.com/fight-details/df7928de73fc2fe8",
        "http://ufcstats.com/fight-details/5c783cd188425783",
        "http://ufcstats.com/fight-details/bde635a4f345bc3e",
        "http://ufcstats.com/fight-details/6114076c689e8457",
    ]
    fight_ids = [get_uuid_string(fight_url) for fight_url in fight_urls]
    fights = ", ".join(fight_ids)

    expected_response = Event(
        scraped_at="2000-01-01 00:00:00 UTC",
        event_id=event_id,
        url="http://www.ufcstats.com/event_response_valid",
        name="UFC 308: Topuria vs. Holloway",
        date="October 26, 2024",
        date_formatted="2024-10-26",
        city="Abu Dhabi",
        state="Abu Dhabi",
        country="United Arab Emirates",
        fights=fights,
    )

    assert parsed_response == expected_response
