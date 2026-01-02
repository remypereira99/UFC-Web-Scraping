from freezegun import freeze_time
import pytest


from entities import FightStatsByRound
from parsers import FightStatByRoundParser
from tests import FIGHT_RESPONSE_VALID_PATH
from tests.utils import load_html_response_from_file
from utils import get_uuid_string


@pytest.fixture
def fight_stat_by_round_parser_valid() -> FightStatByRoundParser:
    fight_stat_by_round_response = load_html_response_from_file(
        FIGHT_RESPONSE_VALID_PATH
    )

    return FightStatByRoundParser(fight_stat_by_round_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_fight_stat_by_round_parse_response_valid(
    fight_stat_by_round_parser_valid: FightStatByRoundParser,
) -> None:
    parsed_response = list(fight_stat_by_round_parser_valid.parse_response())

    fight_id = get_uuid_string("http://ufcstats.com/fight_response_valid")
    fighter_1_id = get_uuid_string(
        "http://ufcstats.com/fighter-details/d661ce4da776fc20"
    )
    fighter_1_fight_stat_by_round_ids = [
        get_uuid_string(fight_id + fighter_1_id + str(round)) for round in range(1, 6)
    ]
    fighter_2_id = get_uuid_string(
        "http://ufcstats.com/fighter-details/aa72b0f831d0bfe5"
    )
    fighter_2_fight_stat_by_round_ids = [
        get_uuid_string(fight_id + fighter_2_id + str(round)) for round in range(1, 6)
    ]

    expected_response_fighter_1_round_1 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_1_fight_stat_by_round_ids[0],
        fight_id=fight_id,
        fighter_id=fighter_1_id,
        round=1,
        total_strikes_landed=42,
        total_strikes_attempted=42,
        significant_strikes_landed=6,
        significant_strikes_attempted=6,
        significant_strikes_landed_head=5,
        significant_strikes_attempted_head=5,
        significant_strikes_landed_body=0,
        significant_strikes_attempted_body=0,
        significant_strikes_landed_leg=1,
        significant_strikes_attempted_leg=1,
        significant_strikes_landed_distance=1,
        significant_strikes_attempted_distance=1,
        significant_strikes_landed_clinch=1,
        significant_strikes_attempted_clinch=1,
        significant_strikes_landed_ground=4,
        significant_strikes_attempted_ground=4,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=0,
        control_time_minutes=2,
        control_time_seconds=21,
        submissions_attempted=0,
        reversals=1,
    )

    expected_response_fighter_1_round_2 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_1_fight_stat_by_round_ids[1],
        fight_id=fight_id,
        fighter_id=fighter_1_id,
        round=2,
        total_strikes_landed=32,
        total_strikes_attempted=49,
        significant_strikes_landed=32,
        significant_strikes_attempted=49,
        significant_strikes_landed_head=12,
        significant_strikes_attempted_head=26,
        significant_strikes_landed_body=6,
        significant_strikes_attempted_body=6,
        significant_strikes_landed_leg=14,
        significant_strikes_attempted_leg=17,
        significant_strikes_landed_distance=31,
        significant_strikes_attempted_distance=48,
        significant_strikes_landed_clinch=1,
        significant_strikes_attempted_clinch=1,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=1,
        takedowns_attempted=1,
        control_time_minutes=0,
        control_time_seconds=2,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_1_round_3 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_1_fight_stat_by_round_ids[2],
        fight_id=fight_id,
        fighter_id=fighter_1_id,
        round=3,
        total_strikes_landed=28,
        total_strikes_attempted=44,
        significant_strikes_landed=21,
        significant_strikes_attempted=36,
        significant_strikes_landed_head=16,
        significant_strikes_attempted_head=28,
        significant_strikes_landed_body=1,
        significant_strikes_attempted_body=3,
        significant_strikes_landed_leg=4,
        significant_strikes_attempted_leg=5,
        significant_strikes_landed_distance=18,
        significant_strikes_attempted_distance=32,
        significant_strikes_landed_clinch=2,
        significant_strikes_attempted_clinch=2,
        significant_strikes_landed_ground=1,
        significant_strikes_attempted_ground=2,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=0,
        control_time_minutes=0,
        control_time_seconds=54,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_1_round_4 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_1_fight_stat_by_round_ids[3],
        fight_id=fight_id,
        fighter_id=fighter_1_id,
        round=4,
        total_strikes_landed=50,
        total_strikes_attempted=65,
        significant_strikes_landed=25,
        significant_strikes_attempted=40,
        significant_strikes_landed_head=19,
        significant_strikes_attempted_head=33,
        significant_strikes_landed_body=5,
        significant_strikes_attempted_body=5,
        significant_strikes_landed_leg=1,
        significant_strikes_attempted_leg=2,
        significant_strikes_landed_distance=21,
        significant_strikes_attempted_distance=35,
        significant_strikes_landed_clinch=4,
        significant_strikes_attempted_clinch=5,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=0,
        control_time_minutes=0,
        control_time_seconds=4,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_1_round_5 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_1_fight_stat_by_round_ids[4],
        fight_id=fight_id,
        fighter_id=fighter_1_id,
        round=5,
        total_strikes_landed=38,
        total_strikes_attempted=63,
        significant_strikes_landed=37,
        significant_strikes_attempted=62,
        significant_strikes_landed_head=26,
        significant_strikes_attempted_head=50,
        significant_strikes_landed_body=6,
        significant_strikes_attempted_body=7,
        significant_strikes_landed_leg=5,
        significant_strikes_attempted_leg=5,
        significant_strikes_landed_distance=32,
        significant_strikes_attempted_distance=56,
        significant_strikes_landed_clinch=5,
        significant_strikes_attempted_clinch=6,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=3,
        control_time_minutes=0,
        control_time_seconds=0,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_2_round_1 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_2_fight_stat_by_round_ids[0],
        fight_id=fight_id,
        fighter_id=fighter_2_id,
        round=1,
        total_strikes_landed=1,
        total_strikes_attempted=1,
        significant_strikes_landed=1,
        significant_strikes_attempted=1,
        significant_strikes_landed_head=0,
        significant_strikes_attempted_head=0,
        significant_strikes_landed_body=1,
        significant_strikes_attempted_body=1,
        significant_strikes_landed_leg=0,
        significant_strikes_attempted_leg=0,
        significant_strikes_landed_distance=1,
        significant_strikes_attempted_distance=1,
        significant_strikes_landed_clinch=0,
        significant_strikes_attempted_clinch=0,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=1,
        takedowns_attempted=2,
        control_time_minutes=1,
        control_time_seconds=58,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_2_round_2 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_2_fight_stat_by_round_ids[1],
        fight_id=fight_id,
        fighter_id=fighter_2_id,
        round=2,
        total_strikes_landed=10,
        total_strikes_attempted=30,
        significant_strikes_landed=10,
        significant_strikes_attempted=30,
        significant_strikes_landed_head=6,
        significant_strikes_attempted_head=21,
        significant_strikes_landed_body=3,
        significant_strikes_attempted_body=7,
        significant_strikes_landed_leg=1,
        significant_strikes_attempted_leg=2,
        significant_strikes_landed_distance=10,
        significant_strikes_attempted_distance=29,
        significant_strikes_landed_clinch=0,
        significant_strikes_attempted_clinch=1,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=3,
        control_time_minutes=0,
        control_time_seconds=0,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_2_round_3 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_2_fight_stat_by_round_ids[2],
        fight_id=fight_id,
        fighter_id=fighter_2_id,
        round=3,
        total_strikes_landed=13,
        total_strikes_attempted=25,
        significant_strikes_landed=13,
        significant_strikes_attempted=25,
        significant_strikes_landed_head=4,
        significant_strikes_attempted_head=15,
        significant_strikes_landed_body=6,
        significant_strikes_attempted_body=7,
        significant_strikes_landed_leg=3,
        significant_strikes_attempted_leg=3,
        significant_strikes_landed_distance=13,
        significant_strikes_attempted_distance=25,
        significant_strikes_landed_clinch=0,
        significant_strikes_attempted_clinch=0,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=1,
        takedowns_attempted=1,
        control_time_minutes=0,
        control_time_seconds=6,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_2_round_4 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_2_fight_stat_by_round_ids[3],
        fight_id=fight_id,
        fighter_id=fighter_2_id,
        round=4,
        total_strikes_landed=14,
        total_strikes_attempted=30,
        significant_strikes_landed=14,
        significant_strikes_attempted=30,
        significant_strikes_landed_head=4,
        significant_strikes_attempted_head=15,
        significant_strikes_landed_body=8,
        significant_strikes_attempted_body=12,
        significant_strikes_landed_leg=2,
        significant_strikes_attempted_leg=3,
        significant_strikes_landed_distance=12,
        significant_strikes_attempted_distance=26,
        significant_strikes_landed_clinch=2,
        significant_strikes_attempted_clinch=4,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=2,
        control_time_minutes=0,
        control_time_seconds=55,
        submissions_attempted=0,
        reversals=0,
    )

    expected_response_fighter_2_round_5 = FightStatsByRound(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_stat_by_round_id=fighter_2_fight_stat_by_round_ids[4],
        fight_id=fight_id,
        fighter_id=fighter_2_id,
        round=5,
        total_strikes_landed=15,
        total_strikes_attempted=33,
        significant_strikes_landed=15,
        significant_strikes_attempted=33,
        significant_strikes_landed_head=9,
        significant_strikes_attempted_head=24,
        significant_strikes_landed_body=6,
        significant_strikes_attempted_body=9,
        significant_strikes_landed_leg=0,
        significant_strikes_attempted_leg=0,
        significant_strikes_landed_distance=13,
        significant_strikes_attempted_distance=31,
        significant_strikes_landed_clinch=2,
        significant_strikes_attempted_clinch=2,
        significant_strikes_landed_ground=0,
        significant_strikes_attempted_ground=0,
        knockdowns=0,
        takedowns_landed=0,
        takedowns_attempted=0,
        control_time_minutes=0,
        control_time_seconds=1,
        submissions_attempted=0,
        reversals=0,
    )

    assert parsed_response[0] == expected_response_fighter_1_round_1
    assert parsed_response[1] == expected_response_fighter_1_round_2
    assert parsed_response[2] == expected_response_fighter_1_round_3
    assert parsed_response[3] == expected_response_fighter_1_round_4
    assert parsed_response[4] == expected_response_fighter_1_round_5

    assert parsed_response[5] == expected_response_fighter_2_round_1
    assert parsed_response[6] == expected_response_fighter_2_round_2
    assert parsed_response[7] == expected_response_fighter_2_round_3
    assert parsed_response[8] == expected_response_fighter_2_round_4
    assert parsed_response[9] == expected_response_fighter_2_round_5
