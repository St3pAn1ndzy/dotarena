import { useState, useEffect } from "react"
import type { MatchSummary } from "../api/matches"
import { fetchMatches } from "../api/matches"

const MOCK_MATCHES: MatchSummary[] = [
  {
    match_id: 9103785233,
    hero_id: 74,
    kills: 12,
    deaths: 3,
    assists: 8,
    radiant_win: false,
    game_mode: 22,
    duration: 1680,
    start_time: Math.floor(Date.now() / 1000) - 3600,
  },
  {
    match_id: 9102741708,
    hero_id: 2,
    kills: 5,
    deaths: 7,
    assists: 15,
    radiant_win: false,
    game_mode: 22,
    duration: 2210,
    start_time: Math.floor(Date.now() / 1000) - 7200,
  },
  {
    match_id: 9102674841,
    hero_id: 89,
    kills: 8,
    deaths: 2,
    assists: 10,
    radiant_win: true,
    game_mode: 22,
    duration: 2599,
    start_time: Math.floor(Date.now() / 1000) - 10800,
  },
]

export function useFetchMatches(steamId: string) {
  const [data, setData] = useState<MatchSummary[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const id = Number(steamId)
    if (isNaN(id)) {
      setData(MOCK_MATCHES)
      setLoading(false)
      return
    }

    fetchMatches(id)
      .then((result) => {
        if (result.length === 0) {
          setData(MOCK_MATCHES)
        } else {
          setData(result)
        }
      })
      .catch(() => setData(MOCK_MATCHES))
      .finally(() => setLoading(false))
  }, [steamId])

  return { data, loading, error }
}