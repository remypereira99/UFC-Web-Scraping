from tests.utils import load_html_response_from_file

import pytest

from . import FIGHTER_RESPONSE_VALID_PATH
from entities import Fighter
from parsers import FighterInfoParser


@pytest.fixture
def fighter_info_parser_valid() -> FighterInfoParser:
    fighter_response = load_html_response_from_file(FIGHTER_RESPONSE_VALID_PATH)

    return FighterInfoParser(fighter_response)


def test_fighter_info_parse_response_valid(
    fighter_info_parser_valid: FighterInfoParser,
) -> None:
    parsed_response = fighter_info_parser_valid.parse_response()

    expected_response = Fighter(
        fighter_id="f35bdc9b-f835-5992-ae94-48ea5429275a",
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
        dob="1990-12-20",
        record="27-9-0",
        wins=27,
        losses=9,
        draws=0,
        no_contests=0,
        opponents="66d48dc7-da46-54bf-8eed-011be1485b5a, 388259b0-1c58-5960-b225-a4ee9eb354a1, 66d48dc7-da46-54bf-8eed-011be1485b5a, 8d4acecd-f975-566b-a10e-585621f31688, 66d48dc7-da46-54bf-8eed-011be1485b5a, 10775baa-e6db-5ccc-bc65-85b1ab654b57, 66d48dc7-da46-54bf-8eed-011be1485b5a, 371a9460-9ac6-54c2-8600-2ae8b8e1538b, 66d48dc7-da46-54bf-8eed-011be1485b5a, 250aaa0d-deaf-5dff-9601-c244555edb6b, 66d48dc7-da46-54bf-8eed-011be1485b5a, fdc2b8a8-4418-5992-90a4-b11621b4f6b5, 66d48dc7-da46-54bf-8eed-011be1485b5a, 9c9ff3ac-399e-5f89-ba30-acd5a8e3c62a, 66d48dc7-da46-54bf-8eed-011be1485b5a, 49d27e53-c9e6-59f6-ac0e-c70129316258, 66d48dc7-da46-54bf-8eed-011be1485b5a, d784dec5-60f2-5fb7-b6e9-1dd4d04e41ed, 66d48dc7-da46-54bf-8eed-011be1485b5a, 393711bb-ef5c-5ab5-8d9b-ef8de0c9fa77, 66d48dc7-da46-54bf-8eed-011be1485b5a, 9c9ff3ac-399e-5f89-ba30-acd5a8e3c62a, 66d48dc7-da46-54bf-8eed-011be1485b5a, de76b42d-a4ed-5562-b039-4a70cc94fa6f, 66d48dc7-da46-54bf-8eed-011be1485b5a, de76b42d-a4ed-5562-b039-4a70cc94fa6f, 66d48dc7-da46-54bf-8eed-011be1485b5a, e67ea6df-c424-5d14-8e41-c63e1580b9f8, 66d48dc7-da46-54bf-8eed-011be1485b5a, d833894a-ac70-58b6-b135-5fd35820a02d, 66d48dc7-da46-54bf-8eed-011be1485b5a, 4bac55b0-c36b-535f-b701-ffeff246b779, 66d48dc7-da46-54bf-8eed-011be1485b5a, 7e5a2c8d-b1de-5472-9961-e9ba5082c2a6, 66d48dc7-da46-54bf-8eed-011be1485b5a, f61e0f81-ab82-5831-b36f-0acd30f62406, 66d48dc7-da46-54bf-8eed-011be1485b5a, 0f0ed865-43d3-552e-9346-a9b1a1dd042d, 66d48dc7-da46-54bf-8eed-011be1485b5a, 46a27c57-aa27-5c62-b9e4-385a09390d9f, 66d48dc7-da46-54bf-8eed-011be1485b5a, 40ad3d37-4a57-5e13-94ae-2f97325da82f, 66d48dc7-da46-54bf-8eed-011be1485b5a, 490e159a-4b43-5d5e-b825-6160515ecb82, 66d48dc7-da46-54bf-8eed-011be1485b5a, 9542ea1e-eebc-543c-8127-2719f9790f93, 66d48dc7-da46-54bf-8eed-011be1485b5a, 55ec5052-003b-5e10-9016-774bf3cc8f1d",
    )

    assert parsed_response == expected_response
