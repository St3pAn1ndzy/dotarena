import { Link } from 'react-router-dom'
import styles from './HomePage.module.css'

function HomePage() {
  return (
    <div>
      <h1 className={styles.title}>DOTARENA</h1>
      <nav className={styles.nav}>
        <Link className={styles.link} to="/profile/123">Профиль →</Link>
        <Link className={styles.link} to="/battle/1">Создать баттл →</Link>
      </nav>
    </div>
  )
}

export default HomePage