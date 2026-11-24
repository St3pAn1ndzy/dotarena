import { useState, useEffect } from "react"
import type { PlayerProfile } from "../api/profile"
import { fetchProfile } from "../api/profile"

const MOCK_PROFILE: PlayerProfile = {
  steam_id: 70388657,
  nickname: "Dendi",
  avatar: "https://avatars.steamstatic.com/1c2143b6f5d6d74f9941d35fdb2556cf0dd0605b_full.jpg",
  rank_tier: 80,
  leaderboard_rank: 2047,
  mmr: 4464.56,
}

export function useFetchProfile(steamId: string) {
  const [data, setData] = useState<PlayerProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const id = Number(steamId)
    if (isNaN(id)) {
      setData(MOCK_PROFILE)  // <- показываем мок вместо ошибки
      setLoading(false)
      return
    }

  fetchProfile(id)
      .then(setData)
      .catch(() => setData(MOCK_PROFILE))  // <- мок при ошибке
      .finally(() => setLoading(false))
  }, [steamId])

  return { data, loading, error }
}