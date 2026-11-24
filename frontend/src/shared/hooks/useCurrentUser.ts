import { useState, useEffect } from "react"
import type { CurrentUser } from "../api/auth"
import { fetchCurrentUser } from "../api/auth"

export function useCurrentUser() {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetchCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  return { user, loading, refetch: () => fetchCurrentUser().then(setUser) }
}