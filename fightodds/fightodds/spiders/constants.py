"""Constants file for spider classes."""

FIGHTODDS_API_URL = "https://api.fightodds.io/gql"

FIGHTODDS_API_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

FIGHTODDS_API_GQL_EVENTS_QUERY = """
query EventsPromotionRecentQuery(
  $promotionSlug: String
  $dateLt: Date
  $dateGte: Date
  $after: String
  $first: Int
  $orderBy: String
) {
  promotion: promotionBySlug(slug: $promotionSlug) {
    events(first: $first, after: $after, date_Gte: $dateGte, date_Lt: $dateLt, orderBy: $orderBy) {
      edges {
        node {
          pk
        }
        cursor
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

FIGHTODDS_API_GQL_EVENT_ODDS_QUERY = """
query EventOddsQuery($eventPk: Int!) {
  eventOfferTable(pk: $eventPk) {
    fightOffers {
      edges {
        node {
          slug
          isCancelled
        }
      }
    }
  }
}
"""

FIGHTODDS_API_GQL_FIGHT_ODDS_QUERY = """
query FightOddsQuery($fightSlug: String) {
  fightOfferTable(slug: $fightSlug) {
    slug
    fighter1 {
      firstName
      lastName
      id
    }
    fighter2 {
      firstName
      lastName
      id
    }
    bestOdds1
    bestOdds2
    straightOffers {
      edges {
        node {
          sportsbook {
            shortName
            slug
          }
          outcome1 {
            odds
            oddsOpen
            oddsBest
            oddsWorst
            oddsPrev
          }
          outcome2 {
            odds
            oddsOpen
            oddsBest
            oddsWorst
            oddsPrev
          }
        }
      }
    }
  }
}
"""

FIGHTODDS_API_GQL_FIGHTERS_LIST_QUERY = """
query FightersListQuery(
  $promotionSlug: String
  $after: String
  $first: Int
) {
  promotion: promotionBySlug(slug: $promotionSlug) {
    fighters(first: $first, after: $after) {
      edges {
        node {
          slug
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

FIGHTODDS_API_GQL_FIGHTER_STATS_QUERY = """
query FighterStatsQuery($fighterSlug: String) {
  fighter: fighterBySlug(slug: $fighterSlug) {
    id
    slug
    firstName
    lastName
    birthDate
    fightingStyle
    nationality
    grapplingStyle {
      edges {
        node {
          name
        }
      }
    }
    height
    reach
    stance
    legReach
  }
}
"""

FIGHTODDS_API_GQL_FIGHTER_QUERY = """
query FighterQuery(
  $fighterSlug: String
) {
  fighter: fighterBySlug(slug: $fighterSlug) {
    ...FighterTabPanelInfo_fighter
    id
  }
}

fragment FighterAge_fighter on FighterNode {
  birthDate
  age
}

fragment FighterCampListStyled_fighter on FighterNode {
  camps {
    edges {
      node {
        name
        id
      }
    }
  }
}

fragment FighterFightingStyle_fighter on FighterNode {
  fightingStyle
}

fragment FighterFlag_fighter on FighterNode {
  nationality
}

fragment FighterFullName_fighter on FighterNode {
  firstName
  lastName
}

fragment FighterGrapplingStyleList_fighter on FighterNode {
  grapplingStyle {
    edges {
      node {
        name
        id
      }
    }
  }
}

fragment FighterHeight_fighter on FighterNode {
  height
}

fragment FighterHistoryList_fighter on FighterNode {
  fightHistory {
    edges {
      node {
        id
        opponent {
          ...FighterAge_fighter
          ...FighterHeight_fighter
          ...FighterReach_fighter
          ...FighterRecord_fighter
          firstName
          lastName
          legReach
          fightingStyle
          stance
          slug
          id
        }
        weightClass
        fighterOdds
        opponentOdds
        eventName
        eventSlug
        eventPk
        result
        methodOfVictory1
        methodOfVictory2
        round
        duration
        date
        promotionLogo
      }
    }
  }
}

fragment FighterLegReach_fighter on FighterNode {
  legReach
}

fragment FighterLosses_fighter on FighterNode {
  koLosses
  subLosses
  decLosses
  dqLosses
}

fragment FighterNationality_fighter on FighterNode {
  nationality
  ...FighterFlag_fighter
}

fragment FighterRankListStyled_fighter on FighterNode {
  ranks {
    edges {
      node {
        fightingStyle {
          name
          id
        }
        rank
        id
      }
    }
  }
}

fragment FighterReach_fighter on FighterNode {
  reach
}

fragment FighterRecord_fighter on FighterNode {
  koWins
  subWins
  decWins
  dqWins
  koLosses
  subLosses
  decLosses
  dqLosses
  draws
}

fragment FighterStance_fighter on FighterNode {
  stance
}

fragment FighterStrikingStyleList_fighter on FighterNode {
  strikingStyle {
    edges {
      node {
        name
        id
      }
    }
  }
}

fragment FighterTabPanelInfo_fighter on FighterNode {
  ...FighterTableInfo_fighter
  ...FighterTableFightingStyle_fighter
  ...FighterTableRecord_fighter
  ...FighterTableHistory_fighter
}

fragment FighterTableFightingStyle_fighter on FighterNode {
  fightingStyle
  stance
  ranks {
    edges {
      node {
        id
      }
    }
  }
  camps {
    edges {
      node {
        id
      }
    }
  }
  ...FighterStrikingStyleList_fighter
  ...FighterGrapplingStyleList_fighter
  ...FighterRankListStyled_fighter
  ...FighterStance_fighter
  ...FighterCampListStyled_fighter
  ...FighterFightingStyle_fighter
}

fragment FighterTableHistory_fighter on FighterNode {
  ...FighterHistoryList_fighter
}

fragment FighterTableInfo_fighter on FighterNode {
  firstName
  lastName
  nickName
  birthDate
  age
  nationality
  height
  weight
  reach
  legReach
  fightingOutOf
  ...FighterNationality_fighter
  ...FighterHeight_fighter
  ...FighterWeight_fighter
  ...FighterReach_fighter
  ...FighterLegReach_fighter
  ...FighterAge_fighter
  ...FighterFullName_fighter
}

fragment FighterTableRecord_fighter on FighterNode {
  koWins
  subWins
  decWins
  dqWins
  koLosses
  subLosses
  decLosses
  dqLosses
  ...FighterWins_fighter
  ...FighterLosses_fighter
  ...FighterRecord_fighter
}

fragment FighterWeight_fighter on FighterNode {
  weight
}

fragment FighterWins_fighter on FighterNode {
  koWins
  subWins
  decWins
  dqWins
}
"""