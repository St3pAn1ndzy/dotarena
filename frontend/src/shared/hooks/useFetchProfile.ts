import { useState, useEffect } from "react"
import type { PlayerProfile } from "../api/profile"
import { fetchProfile } from "../api/profile"

export function useFetchProfile(steamId: string) {
  const [data, setData] = useState<PlayerProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const id = Number(steamId)
    if (isNaN(id)) {
      setError("Invalid Steam ID")
      setLoading(false)
      return
    }

    fetchProfile(id)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [steamId])

  return { data, loading, error }
}