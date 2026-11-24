export function formatRankTier(rankTier: number | null): string {
  if (rankTier == null || rankTier === 0) return "Нет ранга"

  const ranks = [
    "Herald", "Guardian", "Crusader", "Archon",
    "Legend", "Ancient", "Divine", "Immortal",
  ]

  const rank = Math.floor(rankTier / 10) - 1
  const stars = rankTier % 10

  if (rank < 0 || rank >= ranks.length) return `Rank ${rankTier}`

  if (rank === 7) return "Immortal"
  return `${ranks[rank]} ${stars}★`
}