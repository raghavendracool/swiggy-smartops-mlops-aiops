import FoodCard from "../components/FoodCard";
import { cuisineEmoji } from "../utils/distance";

function MenuPage({ selectedRestaurant, products, selectProduct, backToRestaurants }) {
  return (
    <main className="page">
      <button className="text-btn" onClick={backToRestaurants}>
        ← Back to restaurants
      </button>

      <section className="restaurant-banner">
        <div className="restaurant-image large">
          {cuisineEmoji(selectedRestaurant.cuisine_tag)}
        </div>

        <div>
          <h2>{selectedRestaurant.restaurant_name}</h2>
          <p>{selectedRestaurant.cuisine_tag}</p>
          <p>{selectedRestaurant.address}</p>

          <div className="restaurant-meta">
            <span>⭐ {selectedRestaurant.rating}</span>
            <span>{selectedRestaurant.default_prep_minutes} mins</span>
            <span>₹{selectedRestaurant.cost_for_two} for two</span>
          </div>
        </div>
      </section>

      <section className="menu-section">
        <h3>Recommended Menu</h3>

        <div className="menu-list">
          {products.map((product) => (
            <FoodCard
              key={product.product_id}
              product={product}
              onSelect={selectProduct}
            />
          ))}
        </div>
      </section>
    </main>
  );
}

export default MenuPage;