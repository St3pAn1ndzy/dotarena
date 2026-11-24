import { fetchFromApi } from './client'

export interface MatchSummary {
    match_id: number
    hero_id: number
    kills: number
    deaths: number
    assists: number
    radiant_win: boolean
    player_slot: number
    game_mode: number
    duration: number
    start_time: number
}

export function fetchMatches(steamId: string, limit = 20): Promise<MatchSummary[]> {
    return fetchFromApi(`/profile/${steamId}/matches?limit=${limit}`)
}