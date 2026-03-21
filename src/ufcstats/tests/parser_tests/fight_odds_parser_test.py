from freezegun import freeze_time
import pytest

from entities import FightOdds
from ufc_scraper.parsers.fight_odds_parser import FightOddsParser
from tests import FIGHT_ODDS_RESPONSE_VALID_PATH
from tests.utils import load_json_response_from_file
from utils import get_uuid_string


@pytest.fixture
def fight_odds_parser_valid() -> FightOddsParser:
    fight_odds_response = load_json_response_from_file(FIGHT_ODDS_RESPONSE_VALID_PATH)

    return FightOddsParser(fight_odds_response)


@freeze_time("2000-01-01 00:00:00", tz_offset=0)
def test_fight_odds_parse_response_valid(
    fight_odds_parser_valid: FightOddsParser,
) -> None:
    parsed_response = list(fight_odds_parser_valid.parse_response())

    assert len(parsed_response) == 2

    fight_slug = "jones-vs-aspinall-66300"
    fighter_1_id = "RmlnaHRlck5vZGU6MQ=="
    fighter_2_id = "RmlnaHRlck5vZGU6Mg=="

    draftkings_id = get_uuid_string(fight_slug + "draftkings", should_format_href=False)
    betmgm_id = get_uuid_string(fight_slug + "betmgm", should_format_href=False)

    expected_draftkings = FightOdds(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_odds_id=draftkings_id,
        fight_slug=fight_slug,
        fighter_1_id=fighter_1_id,
        fighter_1_first_name="Jon",
        fighter_1_last_name="Jones",
        fighter_2_id=fighter_2_id,
        fighter_2_first_name="Tom",
        fighter_2_last_name="Aspinall",
        best_odds_1=-175,
        best_odds_2=145,
        sportsbook_short_name="DraftKings",
        sportsbook_slug="draftkings",
        outcome_1_odds=-180,
        outcome_1_odds_open=-200,
        outcome_1_odds_best=-175,
        outcome_1_odds_worst=-210,
        outcome_1_odds_prev=-185,
        outcome_2_odds=150,
        outcome_2_odds_open=165,
        outcome_2_odds_best=155,
        outcome_2_odds_worst=140,
        outcome_2_odds_prev=145,
    )

    expected_betmgm = FightOdds(
        scraped_at="2000-01-01 00:00:00 UTC",
        fight_odds_id=betmgm_id,
        fight_slug=fight_slug,
        fighter_1_id=fighter_1_id,
        fighter_1_first_name="Jon",
        fighter_1_last_name="Jones",
        fighter_2_id=fighter_2_id,
        fighter_2_first_name="Tom",
        fighter_2_last_name="Aspinall",
        best_odds_1=-175,
        best_odds_2=145,
        sportsbook_short_name="BetMGM",
        sportsbook_slug="betmgm",
        outcome_1_odds=-175,
        outcome_1_odds_open=-190,
        outcome_1_odds_best=-170,
        outcome_1_odds_worst=-200,
        outcome_1_odds_prev=-180,
        outcome_2_odds=145,
        outcome_2_odds_open=160,
        outcome_2_odds_best=150,
        outcome_2_odds_worst=135,
        outcome_2_odds_prev=140,
    )

    assert parsed_response[0] == expected_draftkings
    assert parsed_response[1] == expected_betmgm
