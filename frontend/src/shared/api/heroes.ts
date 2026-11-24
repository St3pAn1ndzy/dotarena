import { fetchFromApi } from './client'

export interface HeroStats {
  hero_id: number
  games: number
  win: number
  kills: number
  deaths: number
  assists: number
  last_played: number
}

export function fetchHeroes(steamId: string): Promise<HeroStats[]> {
  return fetchFromApi(`/profile/${steamId}/heroes`)
}