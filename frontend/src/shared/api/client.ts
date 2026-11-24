const BASE_URL = "/api"

export async function fetchFromApi<T>(path: string): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`)
    if (!res.ok) {
        throw new Error(`API error: ${res.status}`)
    }
    return res.json()
}