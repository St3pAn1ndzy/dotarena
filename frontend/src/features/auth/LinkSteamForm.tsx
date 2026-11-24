import { useState } from "react"
import type { CurrentUser } from "../../shared/api/auth"
import { linkSteam } from "../../shared/api/auth"
import styles from "./LinkSteamForm.module.css"

interface Props {
  user: CurrentUser
  onLinked: (user: CurrentUser) => void
}

export default function LinkSteamForm({ user, onLinked }: Props) {
  const [input, setInput] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setLoading(true)
    setError(null)
    try {
      const updated = await linkSteam(input.trim())
      onLinked(updated)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Привязать Steam</h3>
      <p className={styles.description}>
        Введите ваш Steam ID (число) или ссылку на профиль
      </p>
      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          className={styles.input}
          type="text"
          placeholder="Steam ID или ссылка"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Сохранение..." : "Привязать"}
        </button>
      </form>
      {error && <p className={styles.error}>{error}</p>}
    </div>
  )
}