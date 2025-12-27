"""Utility functions for UFC data scraping and normalization."""

import re
from typing import List, Tuple
from uuid import uuid5, NAMESPACE_URL


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


def get_strikes_landed_attempted(fight_stat: str) -> Tuple[int, int]:
    """Get strikes landed and attempted from fight stat string.

    Args:
        fight_stat (str): Fight stat with the format "X of Y"

    Returns:
        tuple[int, int]: A tuple of strikes (landed, attempted)

    Raises:
        ValueError: If fight_stat does not match the format "X of Y"

    """
    strikes_attempted_landed_pattern = re.compile(r"^\d+\s+of\s+\d+$")
    fight_stat_clean = clean_string(fight_stat)
    if not strikes_attempted_landed_pattern.fullmatch(fight_stat_clean):
        raise ValueError(
            f"Invalid fight_stat format: {fight_stat!r}. Expected 'X of Y'."
        )
    fight_stat_split: List[str] = fight_stat_clean.split(" of ")
    landed = int(fight_stat_split[0])
    attempted = int(fight_stat_split[1])

    return landed, attempted
