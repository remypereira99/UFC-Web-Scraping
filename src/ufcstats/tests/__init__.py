from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent / "fixtures" / "responses"
FIGHT_RESPONSE_VALID_PATH = BASE_PATH / "fights" / "fight_response_valid.html"
FIGHTER_RESPONSE_VALID_PATH = BASE_PATH / "fighters" / "fighter_response_valid.html"
EVENT_RESPONSE_VALID_PATH = BASE_PATH / "events" / "event_response_valid.html"
FIGHT_ODDS_RESPONSE_VALID_PATH = (
    BASE_PATH / "fight_odds" / "fight_odds_response_valid.json"
)
