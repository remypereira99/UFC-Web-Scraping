from collections import defaultdict
import re
from typing import Dict, List, Tuple, Union
from uuid import uuid5, NAMESPACE_URL

from scrapy.http import Response


def clean_string(raw_string: str) -> str:
    """Normalize whitespace in a string.

    Collapses consecutive whitespace characters (spaces, tabs, newlines, etc.)
    into a single space and removes leading and trailing whitespace.

    Args:
        raw_string (str): The input string to clean.

    Returns:
        str: The cleaned string with normalized whitespace.

    """
    return re.sub(r"\s+", " ", raw_string).strip()


def get_uuid_string(input_string: str) -> str:
    """Generate a deterministic UUID string from an input string.

    Uses UUID version 5 (SHA-1 based) with the URL namespace to produce
    a stable, deterministic UUID.

    Args:
        input_string (str): The input string used to generate the UUID.

    Returns:
        str: The generated UUID represented as a string.

    """
    return str(uuid5(namespace=NAMESPACE_URL, name=input_string))


def get_judges_decisions(response: Response) -> Dict[str, Union[str, int]]:
    judge_decision_dict: defaultdict[str, Union[str, int]] = defaultdict()

    judges_raw: List[str] = (
        response.css("i.b-fight-details__text-item").xpath("./span/text()").getall()[1:]
    )
    judges_clean: List[str] = [clean_string(judge) for judge in judges_raw]
    judge_decision_dict["judge_a"] = judges_clean[0]
    judge_decision_dict["judge_b"] = judges_clean[1]
    judge_decision_dict["judge_c"] = judges_clean[2]

    score_regex = r"\d{2} - \d{2}\."
    scores_raw: List[str] = response.css("i.b-fight-details__text-item::text").getall()
    scores_clean: List[str] = [
        clean_string(score).replace(".", "")
        for score in scores_raw
        if re.search(score_regex, score)
    ]
    judge_a_score, judge_b_score, judge_c_score = scores_clean
    judge_scores = zip(
        ["judge_a", "judge_b", "judge_c"], [judge_a_score, judge_b_score, judge_c_score]
    )
    for judge, score in judge_scores:
        judge_decision_dict[f"{judge}_fighter_1_score"] = int(score.split(" - ")[0])
        judge_decision_dict[f"{judge}_fighter_2_score"] = int(score.split(" - ")[1])

    return judge_decision_dict


def get_fight_stats_from_summary(fight_stat_summary: str) -> Tuple[int, int]:
    fight_stat_summary_split: List[str] = clean_string(fight_stat_summary).split(" of ")
    landed = int(fight_stat_summary_split[0])
    attempted = int(fight_stat_summary_split[1])

    return landed, attempted
