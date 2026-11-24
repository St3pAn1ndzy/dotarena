const BASE_URL = "/api"

function getInitData(): string {
  try {
    return (window as any).Telegram?.WebApp?.initData ?? ""
  } catch {
    return ""
  }
}

export async function fetchFromApi<T>(path: string): Promise<T> {
  const headers: Record<string, string> = {}
  const initData = getInitData()
  if (initData) {
    headers["Authorization"] = initData
  }

  const res = await fetch(`${BASE_URL}${path}`, { headers })
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`)
  }
  return res.json()
}

export async function fetchFromApiWithBody<T>(path: string, method: string, body: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  const initData = getInitData()
  if (initData) {
    headers["Authorization"] = initData
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`)
  }
  return res.json()
}