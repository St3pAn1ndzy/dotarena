import heroMap from "./heroes.json"

const CDN_BASE = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes"

export function getHeroName(id: number): string {
  return (heroMap as Record<number, string>)[id] ?? "unknown"
}

export function getHeroIconUrl(id: number): string {
  const name = getHeroName(id)
  return `${CDN_BASE}/${name}.png`
}