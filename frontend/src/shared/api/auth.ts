import { fetchFromApi, fetchFromApiWithBody } from './client'

export interface CurrentUser {
  id: number
  telegram_id: number
  steam_id: number | null
  nickname: string | null
  avatar_url: string | null
}

export function fetchCurrentUser(): Promise<CurrentUser> {
  return fetchFromApi('/auth/me')
}

export function linkSteam(steamId: string): Promise<CurrentUser> {
  return fetchFromApiWithBody('/auth/steam', 'PUT', { steam_id: steamId })
}