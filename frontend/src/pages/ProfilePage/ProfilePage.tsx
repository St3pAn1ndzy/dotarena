import { useParams } from 'react-router-dom'
import { useFetchProfile } from '../../shared/hooks/useFetchProfile'
import { useFetchMatches } from '../../shared/hooks/useFetchMatches'
import { useFetchHeroes } from '../../shared/hooks/useFetchHeroes'
import { useCurrentUser } from '../../shared/hooks/useCurrentUser'
import PlayerCard from '../../features/profile/PlayerCard'
import MatchList from '../../features/matches/MatchList'
import TopHeroes from '../../features/heroes/TopHeroes'
import PlayerStats from '../../features/stats/PlayerStats'
import LinkSteamForm from '../../features/auth/LinkSteamForm'
import styles from './ProfilePage.module.css'

export default function ProfilePage() {
  const { steamId } = useParams<{ steamId: string }>()
  const { user, refetch } = useCurrentUser()
  const { data: profile, loading: profileLoading, error: profileError } = useFetchProfile(steamId || '')
  const { data: matches, loading: matchesLoading } = useFetchMatches(steamId || '')
  const { data: heroes } = useFetchHeroes(steamId || '')

  if (profileLoading) return <div className={styles.container}><p>Загрузка...</p></div>
  if (profileError) return <div className={styles.container}><p className={styles.error}>Ошибка: {profileError}</p></div>

  // Показываем форму привязки, если пользователь залогинен и у него нет steam_id
  const showLinkForm = user && !user.steam_id

  return (
    <div className={styles.container}>
      {profile && <PlayerCard profile={profile} />}
      {showLinkForm && <LinkSteamForm user={user} onLinked={refetch} />}
      {matches && matches.length > 0 && <PlayerStats matches={matches} />}
      {heroes && heroes.length > 0 && <TopHeroes heroes={heroes} />}
      {matches && <MatchList matches={matches} />}
      {matchesLoading && <p>Загрузка матчей...</p>}
    </div>
  )
}