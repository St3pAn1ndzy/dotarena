import styles from './BattlePage.module.css'

function BattlePage() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Баттл</h1>
      <p className={styles.text}>Счёт: скоро</p>
    </div>
  )
}

export default BattlePage