import RestaurantCard from "../components/RestaurantCard";

function RestaurantsPage({ restaurants, selectedAddress, selectRestaurant }) {
  return (
    <main className="page">
      <section className="page-title">
        <h2>Restaurants Near {selectedAddress.area}</h2>
        <p>Distance is calculated from the selected delivery address.</p>
      </section>

      <div className="restaurant-list">
        {restaurants.map((restaurant) => (
          <RestaurantCard
            key={restaurant.restaurant_id}
            restaurant={restaurant}
            selectedAddress={selectedAddress}
            onSelect={selectRestaurant}
          />
        ))}
      </div>
    </main>
  );
}

export default RestaurantsPage;