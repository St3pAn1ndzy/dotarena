import { useState, useEffect } from "react"
import type { MatchSummary } from "../api/matches"
import { fetchMatches } from "../api/matches"

export function useFetchMatches(steamId: string) {
  const [data, setData] = useState<MatchSummary[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)

    fetchMatches(steamId)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [steamId])

  return { data, loading, error }
}