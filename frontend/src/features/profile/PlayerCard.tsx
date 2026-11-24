import type { PlayerProfile } from "../../shared/api/profile"
import styles from "./PlayerCard.module.css"

interface Props {
  profile: PlayerProfile
}

export default function PlayerCard({ profile }: Props) {
  return (
    <div className={styles.card}>
      {profile.avatar && (
        <img src={profile.avatar} alt={profile.nickname ?? ""} className={styles.avatar} />
      )}
      <div className={styles.info}>
        <h2 className={styles.nickname}>{profile.nickname}</h2>
        {profile.leaderboard_rank && (
          <p className={styles.leaderboard}>Лидерборд #{profile.leaderboard_rank}</p>
        )}
      </div>
    </div>
  )
}