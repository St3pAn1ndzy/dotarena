import type { MatchSummary } from "../../shared/api/matches"
import styles from "./PlayerStats.module.css"

interface Props {
  matches: MatchSummary[]
}

function isWin(match: MatchSummary): boolean {
  const isRadiant = match.player_slot < 128
  return isRadiant ? match.radiant_win : !match.radiant_win
}

export default function PlayerStats({ matches }: Props) {
  if (matches.length === 0) return null

  const wins = matches.filter(isWin).length
  const total = matches.length
  const winrate = ((wins / total) * 100).toFixed(0)

  const avgKills = (matches.reduce((s, m) => s + m.kills, 0) / total).toFixed(1)
  const avgDeaths = (matches.reduce((s, m) => s + m.deaths, 0) / total).toFixed(1)
  const avgAssists = (matches.reduce((s, m) => s + m.assists, 0) / total).toFixed(1)

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Статистика (последние {total} матчей)</h3>
      <div className={styles.grid}>
        <div className={styles.stat}>
          <span className={styles.value}>{winrate}%</span>
          <span className={styles.label}>Винрейт</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.value}>{avgKills}</span>
          <span className={styles.label}>Убийств</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.value}>{avgDeaths}</span>
          <span className={styles.label}>Смертей</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.value}>{avgAssists}</span>
          <span className={styles.label}>Помощи</span>
        </div>
      </div>
      <div className={styles.winbar}>
        <div className={styles.winbarFill} style={{ width: `${winrate}%` }}>
          {wins}W
        </div>
        <div className={styles.winbarEmpty}>{total - wins}L</div>
      </div>
    </div>
  )
}