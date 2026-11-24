import type { MatchSummary } from "../../shared/api/matches"
import styles from "./MatchList.module.css"
import { getHeroIconUrl } from "../../shared/lib/heroes"

interface Props {
  matches: MatchSummary[]
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, "0")}`
}

function formatTime(unix: number): string {
  const date = new Date(unix * 1000)
  return date.toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function MatchList({ matches }: Props) {
  return (
    <div className={styles.list}>
      <h3 className={styles.title}>Последние матчи</h3>
      {matches.map((m) => (
        <div
          key={m.match_id}
          className={`${styles.match} ${m.radiant_win ? styles.win : styles.lose}`}
        >
          <div className={styles.hero}>
            <img
              src={getHeroIconUrl(m.hero_id)}
              alt={`hero ${m.hero_id}`}
              className={styles.heroIcon}
            />
          </div>
          <div className={styles.kda}>
            {m.kills}/{m.deaths}/{m.assists}
          </div>
          <div className={styles.duration}>{formatDuration(m.duration)}</div>
          <div className={styles.time}>{formatTime(m.start_time)}</div>
          <div className={styles.result}>{m.radiant_win ? "Победа" : "Поражение"}</div>
        </div>
      ))}
    </div>
  )
}