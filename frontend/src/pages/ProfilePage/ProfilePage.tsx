import { useParams } from 'react-router-dom'
import { useFetchProfile } from '../../shared/hooks/useFetchProfile'
import styles from './ProfilePage.module.css'

export default function ProfilePage() {
  const { steamId } = useParams<{ steamId: string }>()
  const { data, loading, error } = useFetchProfile(steamId || '')

  if (loading) return <p>Loading...</p>
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>
  if (!data) return <p>No profile data</p>

  return (
    <div className={styles.container}>
      {data.avatar && <img src={data.avatar} alt="avatar" />}
      <h2>{data.nickname}</h2>
      <p>MMR: {data.mmr?.toFixed(0)}</p>
      <p>Rank tier: {data.rank_tier}</p>
      {data.leaderboard_rank && <p>Leaderboard: #{data.leaderboard_rank}</p>}
    </div>
  )
}