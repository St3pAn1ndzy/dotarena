import { fetchFromApi } from './client'

export interface PlayerProfile {
    steam_id: number
    nickname: string | null
    avatar: string | null
    rank_tier: number | null
    leaderboard_rank: number | null
    mmr: number | null
}

export function fetchProfile(steamId: number): Promise<PlayerProfile> {
    return fetchFromApi(`/profile/${steamId}`)
}