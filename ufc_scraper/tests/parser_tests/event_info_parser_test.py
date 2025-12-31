from freezegun import freeze_time
import pytest

from entities import Event
from parsers import EventInfoParser
from tests import EVENT_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file


@pytest.fixture
def event_info_parser_valid() -> EventInfoParser:
    event_response = load_html_response_from_file(EVENT_RESPONSE_VALID_PATH)

    return EventInfoParser(event_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_event_info_parse_response_valid(
    event_info_parser_valid: EventInfoParser,
) -> None:
    parsed_response = event_info_parser_valid.parse_response()

    expected_response = Event(
        scraped_at="2000-01-01 00:00:00 UTC",
        event_id="42935486-0863-505f-a12f-1f96955a0794",
        url="http://www.ufcstats.com/event_response_valid",
        name="UFC 308: Topuria vs. Holloway",
        date="October 26, 2024",
        date_formatted="2024-10-26",
        city="Abu Dhabi",
        state="Abu Dhabi",
        country="United Arab Emirates",
        fights=(
            "b85fab4f-cbb1-5f54-af41-8f5dec7b2f37, 285d33cd-d7bc-5c1d-8689-beef4d16c610, 644807e9-aa74-53e0-8c49-ee3ce5afda1e, "
            "e6321b03-713b-59a4-bbfe-c93474ea82d5, 9f61f3da-b514-5ea4-aeaf-4282b6be5c23, 83951809-e087-5a84-8705-7a92217e1197, "
            "67029387-1874-5324-942b-549ef16e9746, 65bf1a92-d9f5-5658-9c06-8ec58b1c9e6e, 0282dae7-bb29-57ca-89f2-b51c6bb56cf2, "
            "114c5e2c-4875-5816-b24c-2854c58b92c4, fc5e6c3a-f49a-5b01-b178-a7f61317dc20, 10813345-120b-5df4-ba69-8140a867dafd, "
            "9b1ae4b1-de88-5d7b-9c08-06aac5e7c86a"
        ),
    )

    assert parsed_response == expected_response
