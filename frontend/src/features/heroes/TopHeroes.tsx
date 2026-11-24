import type { HeroStats } from "../../shared/api/heroes"
import { getHeroIconUrl } from "../../shared/lib/heroes"
import styles from "./TopHeroes.module.css"

interface Props {
  heroes: HeroStats[]
}

export default function TopHeroes({ heroes }: Props) {
  const top = heroes.slice(0, 5)
  const maxGames = top[0]?.games ?? 1

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Любимые герои</h3>
      <div className={styles.list}>
        {top.map((h) => {
          const winrate = h.games > 0 ? ((h.win / h.games) * 100).toFixed(0) : "0"
          return (
            <div key={h.hero_id} className={styles.item}>
              <img src={getHeroIconUrl(h.hero_id)} alt="" className={styles.icon} />
              <div className={styles.info}>
                <div className={styles.bar}>
                  <div
                    className={styles.barFill}
                    style={{ width: `${(h.games / maxGames) * 100}%` }}
                  />
                </div>
                <div className={styles.stats}>
                  <span>{h.games} игр</span>
                  <span className={styles.winrate}>{winrate}% побед</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}