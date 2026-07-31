import { calcDistanceKm, cuisineEmoji } from "../utils/distance";

function RestaurantCard({ restaurant, selectedAddress, onSelect }) {
  const distance = calcDistanceKm(
    selectedAddress.latitude,
    selectedAddress.longitude,
    restaurant.restaurant_latitude,
    restaurant.restaurant_longitude
  );

  return (
    <div className="restaurant-card" onClick={() => onSelect(restaurant)}>
      <div className="restaurant-image">
        {cuisineEmoji(restaurant.cuisine_tag)}
      </div>

      <div className="restaurant-info">
        <h3>{restaurant.restaurant_name}</h3>
        <p>{restaurant.cuisine_tag} • {restaurant.location_name}</p>
        <p className="muted">{restaurant.address}</p>

        <div className="restaurant-meta">
          <span>⭐ {restaurant.rating}</span>
          <span>{distance} km</span>
          <span>{restaurant.default_prep_minutes} mins</span>
          <span>₹{restaurant.cost_for_two} for two</span>
        </div>
      </div>

      <div className="open-menu">View Menu →</div>
    </div>
  );
}

export default RestaurantCard;