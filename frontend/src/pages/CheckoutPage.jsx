import BillCard from "../components/BillCard";
import { calcDistanceKm } from "../utils/distance";

function CheckoutPage({
  selectedRestaurant,
  selectedProduct,
  selectedAddress,
  checkout,
  setCheckout,
  placeOrder,
  backToMenu,
}) {
  const distance = calcDistanceKm(
    selectedAddress.latitude,
    selectedAddress.longitude,
    selectedRestaurant.restaurant_latitude,
    selectedRestaurant.restaurant_longitude
  );

  return (
    <main className="page checkout-layout">
      <section>
        <button className="text-btn" onClick={backToMenu}>
          ← Back to menu
        </button>

        <h2>Checkout</h2>

        <div className="checkout-card">
          <h3>Delivery Details</h3>

          <p>
            <strong>Deliver to:</strong> {selectedAddress.receiver_name}
          </p>

          <p>{selectedAddress.address_line}</p>

          <p className="muted">
            {selectedAddress.area}, {selectedAddress.city} | {selectedAddress.receiver_type}
          </p>

          <p>
            <strong>Restaurant:</strong> {selectedRestaurant.restaurant_name}
          </p>

          <p>
            <strong>Distance:</strong> {distance} km
          </p>
        </div>

        <div className="checkout-card">
          <h3>Order Options</h3>

          <div className="form-grid">
            <label>
              Quantity
              <input
                type="number"
                min="1"
                value={checkout.quantity}
                onChange={(e) =>
                  setCheckout({ ...checkout, quantity: Number(e.target.value) })
                }
              />
            </label>

            <label>
              Device
              <select
                value={checkout.device_type}
                onChange={(e) =>
                  setCheckout({ ...checkout, device_type: e.target.value })
                }
              >
                <option value="Android">Android</option>
                <option value="iOS">iOS</option>
                <option value="Web">Web</option>
              </select>
            </label>

            <label>
              Surge
              <select
                value={checkout.surge_num}
                onChange={(e) =>
                  setCheckout({ ...checkout, surge_num: Number(e.target.value) })
                }
              >
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </label>

            <label>
              Coupon
              <select
                value={checkout.coupon_used_num}
                onChange={(e) =>
                  setCheckout({ ...checkout, coupon_used_num: Number(e.target.value) })
                }
              >
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </label>
          </div>
        </div>
      </section>

      <BillCard
        selectedRestaurant={selectedRestaurant}
        selectedProduct={selectedProduct}
        checkout={checkout}
        placeOrder={placeOrder}
      />
    </main>
  );
}

export default CheckoutPage;