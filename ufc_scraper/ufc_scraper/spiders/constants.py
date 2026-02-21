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
    events(first: $first, after: $after, start_date: $dateGte, end_date: $dateLt, orderBy: $orderBy) {
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
