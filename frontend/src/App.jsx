import { useEffect, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [user, setUser] = useState(null);

  const [loginForm, setLoginForm] = useState({
    name: "Raghav",
    email: "raghav@example.com",
    membership_tier: "ONE_PLUS",
  });

  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);

  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);

  const [orderOptions, setOrderOptions] = useState({
    city: "Hyderabad",
    device_type: "Android",
    quantity: 1,
    coupon_used_num: 1,
    coupon_discount_amount: 50,
    membership_benefit_amount: 20,
    surge_num: 1,
    raining_num: 1,
    campaign_exposed_num: 1,
    delivery_success_num: 1,
    rating: 4,
    coupon_name: "WELCOME50",
    campaign_name: "Campaign A",
    channel: "Push",
    objective: "Retention",
  });

  const [orderResult, setOrderResult] = useState(null);
  const [myOrders, setMyOrders] = useState([]);
  const [adminOrders, setAdminOrders] = useState([]);

  async function login() {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginForm),
    });

    const data = await response.json();
    setUser(data);
  }

  async function loadRestaurants() {
    const response = await fetch(`${API_BASE}/restaurants`);
    const data = await response.json();
    setRestaurants(data);
  }

  async function loadProducts(restaurant) {
    setSelectedRestaurant(restaurant);

    const response = await fetch(
      `${API_BASE}/restaurants/${restaurant.restaurant_id}/products`
    );

    const data = await response.json();
    setProducts(data);
    setSelectedProduct(null);
  }

  async function placeOrder() {
    if (!user || !selectedRestaurant || !selectedProduct) {
      alert("Please login, select restaurant, and select product");
      return;
    }

    const payload = {
      user_id: user.user_id,
      restaurant_id: selectedRestaurant.restaurant_id,
      product_id: selectedProduct.product_id,
      membership_tier: user.membership_tier,
      ...orderOptions,
    };

    const response = await fetch(`${API_BASE}/orders`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    setOrderResult(data);
    loadMyOrders(user.user_id);
    loadAdminOrders();
  }

  async function loadMyOrders(userId) {
    const response = await fetch(`${API_BASE}/orders/user/${userId}`);
    const data = await response.json();
    setMyOrders(data);
  }

  async function loadAdminOrders() {
    const response = await fetch(`${API_BASE}/admin/orders`);
    const data = await response.json();
    setAdminOrders(data);
  }

  useEffect(() => {
    loadRestaurants();
    loadAdminOrders();
  }, []);

  useEffect(() => {
    if (user) {
      loadMyOrders(user.user_id);
    }
  }, [user]);

  return (
    <div className="app">
      <header className="header">
        <h1>🍔 Mini Swiggy SmartOps</h1>
        <p>Fullstack Swiggy-style app with ML delivery delay prediction</p>
      </header>

      <section className="card">
        <h2>1. Login / Register</h2>

        <div className="grid">
          <input
            value={loginForm.name}
            onChange={(e) =>
              setLoginForm({ ...loginForm, name: e.target.value })
            }
            placeholder="Name"
          />

          <input
            value={loginForm.email}
            onChange={(e) =>
              setLoginForm({ ...loginForm, email: e.target.value })
            }
            placeholder="Email"
          />

          <select
            value={loginForm.membership_tier}
            onChange={(e) =>
              setLoginForm({
                ...loginForm,
                membership_tier: e.target.value,
              })
            }
          >
            <option value="NONE">NONE</option>
            <option value="ONE_LITE">ONE_LITE</option>
            <option value="ONE">ONE</option>
            <option value="ONE_PLUS">ONE_PLUS</option>
          </select>

          <button onClick={login}>Login / Register</button>
        </div>

        {user && (
          <p className="success">
            Logged in as {user.name} | User ID: {user.user_id} | Membership:{" "}
            {user.membership_tier}
          </p>
        )}
      </section>

      <section className="card">
        <h2>2. Select Restaurant</h2>

        <div className="cards">
          {restaurants.map((restaurant) => (
            <div
              key={restaurant.restaurant_id}
              className={
                selectedRestaurant?.restaurant_id === restaurant.restaurant_id
                  ? "mini-card selected"
                  : "mini-card"
              }
              onClick={() => loadProducts(restaurant)}
            >
              <h3>{restaurant.restaurant_name}</h3>
              <p>City: {restaurant.city}</p>
              <p>Cuisine: {restaurant.cuisine_tag}</p>
            </div>
          ))}
        </div>
      </section>

      {products.length > 0 && (
        <section className="card">
          <h2>3. Select Product</h2>

          <div className="cards">
            {products.map((product) => (
              <div
                key={product.product_id}
                className={
                  selectedProduct?.product_id === product.product_id
                    ? "mini-card selected"
                    : "mini-card"
                }
                onClick={() => setSelectedProduct(product)}
              >
                <h3>{product.product_name}</h3>
                <p>Price: ₹{product.price}</p>
                <p>Cuisine: {product.cuisine_tag}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="card">
        <h2>4. Order Options</h2>

        <div className="grid">
          <select
            value={orderOptions.city}
            onChange={(e) =>
              setOrderOptions({ ...orderOptions, city: e.target.value })
            }
          >
            <option value="Hyderabad">Hyderabad</option>
            <option value="Bangalore">Bangalore</option>
          </select>

          <select
            value={orderOptions.device_type}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                device_type: e.target.value,
              })
            }
          >
            <option value="Android">Android</option>
            <option value="iOS">iOS</option>
            <option value="Web">Web</option>
          </select>

          <input
            type="number"
            value={orderOptions.quantity}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                quantity: Number(e.target.value),
              })
            }
            placeholder="Quantity"
          />

          <input
            type="number"
            value={orderOptions.coupon_discount_amount}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                coupon_discount_amount: Number(e.target.value),
              })
            }
            placeholder="Coupon Discount"
          />

          <input
            type="number"
            value={orderOptions.membership_benefit_amount}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                membership_benefit_amount: Number(e.target.value),
              })
            }
            placeholder="Membership Benefit"
          />

          <select
            value={orderOptions.raining_num}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                raining_num: Number(e.target.value),
              })
            }
          >
            <option value={0}>Raining: No</option>
            <option value={1}>Raining: Yes</option>
          </select>

          <select
            value={orderOptions.surge_num}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                surge_num: Number(e.target.value),
              })
            }
          >
            <option value={0}>Surge: No</option>
            <option value={1}>Surge: Yes</option>
          </select>

          <select
            value={orderOptions.coupon_used_num}
            onChange={(e) =>
              setOrderOptions({
                ...orderOptions,
                coupon_used_num: Number(e.target.value),
              })
            }
          >
            <option value={0}>Coupon Used: No</option>
            <option value={1}>Coupon Used: Yes</option>
          </select>

          <button onClick={placeOrder}>Place Order</button>
        </div>
      </section>

      {orderResult && (
        <section className="card result">
          <h2>5. Order Result</h2>

          <p>Order ID: {orderResult.order_id}</p>
          <p>Order Status: {orderResult.order_status}</p>
          <p>Gross Amount: ₹{orderResult.gross_amount}</p>
          <p>Net Amount: ₹{orderResult.net_amount}</p>

          <h3
            className={
              orderResult.delay_risk === "High Delay Risk"
                ? "risk-high"
                : "risk-low"
            }
          >
            {orderResult.delay_risk} | Probability:{" "}
            {orderResult.delay_probability.toFixed(2)}
          </h3>

          <p>{orderResult.recommendation}</p>
        </section>
      )}

      <section className="card">
        <h2>My Orders</h2>

        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>City</th>
              <th>Gross Amount</th>
              <th>Net Amount</th>
              <th>Status</th>
              <th>Delay Risk</th>
              <th>Probability</th>
            </tr>
          </thead>

          <tbody>
            {myOrders.map((order) => (
              <tr key={order.order_id}>
                <td>{order.order_id}</td>
                <td>{order.city}</td>
                <td>{order.gross_amount}</td>
                <td>{order.net_amount}</td>
                <td>{order.order_status}</td>
                <td>{order.delay_risk}</td>
                <td>
                  {order.delay_probability
                    ? order.delay_probability.toFixed(2)
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>Admin - Latest Orders & ML Predictions</h2>

        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>User ID</th>
              <th>City</th>
              <th>Rain</th>
              <th>Surge</th>
              <th>Gross Amount</th>
              <th>Net Amount</th>
              <th>Delay Risk</th>
              <th>Probability</th>
            </tr>
          </thead>

          <tbody>
            {adminOrders.map((order) => (
              <tr key={order.order_id}>
                <td>{order.order_id}</td>
                <td>{order.user_id}</td>
                <td>{order.city}</td>
                <td>{order.raining_num}</td>
                <td>{order.surge_num}</td>
                <td>{order.gross_amount}</td>
                <td>{order.net_amount}</td>
                <td>{order.delay_risk}</td>
                <td>
                  {order.delay_probability
                    ? order.delay_probability.toFixed(2)
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;