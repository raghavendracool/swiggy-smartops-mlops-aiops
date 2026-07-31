import { cuisineEmoji } from "../utils/distance";

function FoodCard({ product, onSelect }) {
  return (
    <div className="food-card">
      <div>
        <span className={product.food_type === "Veg" ? "veg-dot" : "nonveg-dot"} />
        <h4>{product.product_name}</h4>
        <p>₹{product.price}</p>
        <p className="muted">{product.description}</p>
      </div>

      <div className="food-action">
        <div className="food-image">
          {cuisineEmoji(product.cuisine_tag)}
        </div>

        <button className="add-btn" onClick={() => onSelect(product)}>
          ADD
        </button>
      </div>
    </div>
  );
}

export default FoodCard;