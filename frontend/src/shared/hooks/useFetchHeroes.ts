import { useState, useEffect } from "react"
import type { HeroStats } from "../api/heroes"
import { fetchHeroes } from "../api/heroes"

export function useFetchHeroes(steamId: string) {
  const [data, setData] = useState<HeroStats[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)

    fetchHeroes(steamId)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [steamId])

  return { data, loading, error }
}