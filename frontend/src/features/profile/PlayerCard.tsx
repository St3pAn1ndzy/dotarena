import type { PlayerProfile } from "../../shared/api/profile"
import { formatRankTier } from "../../shared/lib/dota"
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
        <p className={styles.mmr}>MMR: {profile.mmr?.toFixed(0) ?? "—"}</p>
        <p className={styles.rank}>{formatRankTier(profile.rank_tier)}</p>
        {profile.leaderboard_rank && (
          <p className={styles.leaderboard}>Leaderboard #{profile.leaderboard_rank}</p>
        )}
      </div>
    </div>
  )
}