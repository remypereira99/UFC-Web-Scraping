"""Constants file for parser classes."""

from typing import List


WEIGHT_CLASSES_LOWER: List[str] = [
    "women's strawweight",
    "women's flyweight",
    "women's bantamweight",
    "women's featherweight",
    "flyweight",
    "bantamweight",
    "featherweight",
    "lightweight",
    "welterweight",
    "middleweight",
    "light heavyweight",
    "heavyweight",
    "catch weight",
    "open weight",
]

TOTALS_STATS_EXPECTED_HEADERS: List[str] = [
    "KD",
    "Sig. str.",
    "Sig. str. %",
    "Total str.",
    "Td",
    "Td %",
    "Sub. att",
    "Rev.",
    "Ctrl",
]
SIGNIFICANT_STRIKES_EXPECTED_HEADERS: List[str] = [
    "Sig. str",
    "Sig. str. %",
    "Head",
    "Body",
    "Leg",
    "Distance",
    "Clinch",
    "Ground",
]
