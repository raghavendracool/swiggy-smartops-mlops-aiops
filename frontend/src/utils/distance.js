export function cuisineEmoji(cuisine) {
  if (cuisine === "Biryani") return "🍛";
  if (cuisine === "Burger") return "🍔";
  if (cuisine === "Chinese") return "🍜";
  if (cuisine === "South Indian") return "🥘";
  if (cuisine === "Desserts") return "🍨";
  if (cuisine === "Bakery") return "🥐";
  return "🍽️";
}

export function calcDistanceKm(lat1, lon1, lat2, lon2) {
  const R = 6371;

  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return Number((R * c).toFixed(2));
}