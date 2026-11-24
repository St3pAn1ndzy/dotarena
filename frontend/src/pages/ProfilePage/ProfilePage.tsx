import { useParams } from 'react-router-dom'
import { useFetchProfile } from '../../shared/hooks/useFetchProfile'
import PlayerCard from '../../features/profile/PlayerCard'
import styles from './ProfilePage.module.css'

export default function ProfilePage() {
  const { steamId } = useParams<{ steamId: string }>()
  const { data, loading, error } = useFetchProfile(steamId || '')

  if (loading) return <div className={styles.container}><p>Загрузка...</p></div>
  if (error) return <div className={styles.container}><p className={styles.error}>Ошибка: {error}</p></div>
  if (!data) return <div className={styles.container}><p>Профиль не найден</p></div>

  return (
    <div className={styles.container}>
      <PlayerCard profile={data} />
    </div>
  )
}