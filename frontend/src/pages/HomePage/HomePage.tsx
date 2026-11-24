import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './HomePage.module.css'

export default function HomePage() {
  const [steamId, setSteamId] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const id = steamId.trim()
    if (id) {
      navigate(`/profile/${id}`)
    }
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>DOTARENA</h1>
      <p className={styles.subtitle}>Введи Steam ID игрока</p>
      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          type="text"
          value={steamId}
          onChange={(e) => setSteamId(e.target.value)}
          placeholder="Например: 70388657"
          className={styles.input}
        />
        <button type="submit" className={styles.button}>Найти</button>
      </form>
    </div>
  )
}