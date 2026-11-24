import { fetchFromApi } from './client'

export interface PlayerProfile {
    steam_id: number
    nickname: string | null
    avatar: string | null
    leaderboard_rank: number | null
}

export function fetchProfile(steamId: string): Promise<PlayerProfile> {
    return fetchFromApi(`/profile/${steamId}`)
}