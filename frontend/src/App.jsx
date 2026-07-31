import { useEffect, useState } from "react";
import "./styles/App.css";

const API_BASE = "http://127.0.0.1:8000";

function cuisineEmoji(cuisine) {
  if (cuisine === "Biryani") return "🍛";
  if (cuisine === "Burger") return "🍔";
  if (cuisine === "Chinese") return "🍜";
  if (cuisine === "South Indian") return "🥘";
  if (cuisine === "Desserts") return "🍨";
  if (cuisine === "Bakery") return "🥐";
  return "🍽️";
}

function calcDistanceKm(lat1, lon1, lat2, lon2) {
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

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "API request failed");
  }

  return data;
}

function App() {
  const [screen, setScreen] = useState("login");
  const [user, setUser] = useState(null);

  const [loginForm, setLoginForm] = useState({
    name: "Raghav",
    email: "raghav@example.com",
    membership_tier: "ONE_PLUS",
  });

  const [currentLocation, setCurrentLocation] = useState({
    latitude: 17.37258711024342,
    longitude: 78.52917012086905,
    locationName: "Demo location, Hyderabad",
    area: "Dilsukhnagar Colony",
    city: "Hyderabad",
    state: "Telangana",
  });

  const [locationStatus, setLocationStatus] = useState(
    "Use current location or demo location"
  );

  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState(null);

  const [addressForm, setAddressForm] = useState({
    receiver_name: "Self",
    receiver_phone: "",
    address_label: "Home",
    address_line: "Dilsukhnagar Colony, Hyderabad",
    area: "Dilsukhnagar Colony",
    city: "Hyderabad",
    state: "Telangana",
    pincode: "500060",
    latitude: 17.37258711024342,
    longitude: 78.52917012086905,
    is_default: 1,
    order_for_someone_else_flag: 0,
    receiver_type: "Self",
  });

  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);

  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);

  const [checkout, setCheckout] = useState({
    quantity: 1,
    device_type: "Android",
    coupon_used_num: 1,
    coupon_discount_amount: 50,
    membership_benefit_amount: 20,
    surge_num: 1,
    campaign_exposed_num: 1,
    delivery_success_num: 1,
    rating: 4,
    coupon_name: "WELCOME50",
    campaign_name: "Campaign A",
    channel: "Push",
    objective: "Retention",
  });

  const [orderResult, setOrderResult] = useState(null);
  const [adminOrders, setAdminOrders] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  async function login() {
    try {
      setErrorMessage("");

      const data = await apiRequest("/login", {
        method: "POST",
        body: JSON.stringify(loginForm),
      });

      setUser(data);
      localStorage.setItem("swiggy_user", JSON.stringify(data));

      await loadAddresses(data.user_id);

      setScreen("location");
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  function logout() {
    localStorage.removeItem("swiggy_user");

    setUser(null);
    setSelectedAddress(null);
    setSelectedRestaurant(null);
    setSelectedProduct(null);
    setOrderResult(null);
    setScreen("login");
  }

  async function reverseLocation(latitude, longitude) {
    try {
      setLocationStatus("Finding readable location...");

      const data = await apiRequest(
        `/location/reverse?latitude=${latitude}&longitude=${longitude}`
      );

      const location = {
        latitude,
        longitude,
        locationName: data.display_name,
        area: data.area,
        city: data.city,
        state: data.state,
      };

      setCurrentLocation(location);
      setLocationStatus(`${data.area}, ${data.city}`);

      setAddressForm((previous) => ({
        ...previous,
        address_line: data.display_name,
        area: data.area,
        city: data.city,
        state: data.state,
        latitude,
        longitude,
      }));
    } catch (error) {
      setLocationStatus("Location name lookup failed, coordinates captured.");

      setCurrentLocation((previous) => ({
        ...previous,
        latitude,
        longitude,
      }));

      setAddressForm((previous) => ({
        ...previous,
        latitude,
        longitude,
      }));
    }
  }

  function getCurrentLocation() {
    if (!navigator.geolocation) {
      setLocationStatus("Browser geolocation is not supported.");
      return;
    }

    setLocationStatus("Requesting location permission...");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        reverseLocation(position.coords.latitude, position.coords.longitude);
      },
      (error) => {
        setLocationStatus(`Location permission failed: ${error.message}`);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  }

  function useHyderabadDemoLocation() {
    reverseLocation(17.37258711024342, 78.52917012086905);
  }

  function useBangaloreDemoLocation() {
    reverseLocation(13.0147, 77.6519);
  }

  async function loadRestaurants() {
    try {
      const data = await apiRequest("/restaurants");
      setRestaurants(data);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  async function loadAddresses(userId) {
    try {
      const data = await apiRequest(`/addresses/user/${userId}`);

      setAddresses(data);

      if (data.length > 0) {
        setSelectedAddress(data[0]);
      }
    } catch (error) {
      setAddresses([]);
    }
  }

  async function saveAddress() {
    try {
      if (!user) {
        alert("Please login first");
        return;
      }

      const payload = {
        user_id: user.user_id,
        ...addressForm,
      };

      const data = await apiRequest("/addresses", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      await loadAddresses(user.user_id);
      setSelectedAddress(data);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  async function selectRestaurant(restaurant) {
    try {
      setSelectedRestaurant(restaurant);
      setSelectedProduct(null);

      const data = await apiRequest(
        `/restaurants/${restaurant.restaurant_id}/products`
      );

      setProducts(data);
      setScreen("menu");
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  function selectProduct(product) {
    setSelectedProduct(product);
    setScreen("checkout");
  }

  async function placeOrder() {
    try {
      if (!user || !selectedAddress || !selectedRestaurant || !selectedProduct) {
        alert("Please complete login, address, restaurant and food selection.");
        return;
      }

      const payload = {
        user_id: user.user_id,
        address_id: selectedAddress.address_id,
        restaurant_id: selectedRestaurant.restaurant_id,
        product_id: selectedProduct.product_id,
        city: selectedAddress.city,
        membership_tier: user.membership_tier,
        raining_num: 0,
        ...checkout,
      };

      const data = await apiRequest("/orders", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setOrderResult(data);
      await loadAdminOrders();
      setScreen("success");
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  async function loadAdminOrders() {
    try {
      const data = await apiRequest("/admin/orders");
      setAdminOrders(data);
    } catch (error) {
      setAdminOrders([]);
    }
  }

  useEffect(() => {
    async function init() {
      const savedUser = localStorage.getItem("swiggy_user");

      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        await loadAddresses(parsedUser.user_id);
        setScreen("location");
      }

      await loadRestaurants();
      await loadAdminOrders();
    }

    init();
  }, []);

  return (
    <div className="app">
      <TopHeader user={user} setScreen={setScreen} logout={logout} />

      {errorMessage && (
        <div className="error-banner">
          <strong>Error:</strong> {errorMessage}
          <button onClick={() => setErrorMessage("")}>×</button>
        </div>
      )}

      {screen !== "login" && (
        <StepBar
          currentScreen={screen}
          setScreen={setScreen}
          user={user}
          selectedAddress={selectedAddress}
          selectedRestaurant={selectedRestaurant}
          selectedProduct={selectedProduct}
        />
      )}

      {screen === "login" && (
        <LoginPage
          loginForm={loginForm}
          setLoginForm={setLoginForm}
          login={login}
        />
      )}

      {screen === "location" && (
        <LocationPage
          currentLocation={currentLocation}
          locationStatus={locationStatus}
          getCurrentLocation={getCurrentLocation}
          useHyderabadDemoLocation={useHyderabadDemoLocation}
          useBangaloreDemoLocation={useBangaloreDemoLocation}
          continueToAddress={() => setScreen("address")}
        />
      )}

      {screen === "address" && (
        <AddressPage
          addresses={addresses}
          selectedAddress={selectedAddress}
          setSelectedAddress={setSelectedAddress}
          addressForm={addressForm}
          setAddressForm={setAddressForm}
          currentLocation={currentLocation}
          saveAddress={saveAddress}
          continueToRestaurants={() => setScreen("restaurants")}
        />
      )}

      {screen === "restaurants" && (
        <RestaurantsPage
          restaurants={restaurants}
          selectedAddress={selectedAddress}
          selectRestaurant={selectRestaurant}
        />
      )}

      {screen === "menu" && (
        <MenuPage
          selectedRestaurant={selectedRestaurant}
          products={products}
          selectProduct={selectProduct}
          backToRestaurants={() => setScreen("restaurants")}
        />
      )}

      {screen === "checkout" && (
        <CheckoutPage
          selectedRestaurant={selectedRestaurant}
          selectedProduct={selectedProduct}
          selectedAddress={selectedAddress}
          checkout={checkout}
          setCheckout={setCheckout}
          placeOrder={placeOrder}
          backToMenu={() => setScreen("menu")}
        />
      )}

      {screen === "success" && orderResult && (
        <OrderSuccessPage
          orderResult={orderResult}
          startAgain={() => {
            setSelectedProduct(null);
            setOrderResult(null);
            setScreen("restaurants");
          }}
          viewAdmin={() => setScreen("admin")}
        />
      )}

      {screen === "admin" && (
        <AdminPage
          adminOrders={adminOrders}
          back={() => setScreen("restaurants")}
        />
      )}
    </div>
  );
}

function TopHeader({ user, setScreen, logout }) {
  return (
    <header className="top-header">
      <div className="brand-section" onClick={() => setScreen(user ? "location" : "login")}>
        <div className="brand-icon">🍔</div>

        <div>
          <h1>Swiggy SmartOps</h1>
          <p>Food ordering with weather, distance and ML delay prediction</p>
        </div>
      </div>

      <div className="header-actions">
        {user && (
          <div className="user-chip">
            <span>👤</span>
            <div>
              <strong>{user.name}</strong>
              <small>{user.membership_tier}</small>
            </div>
          </div>
        )}

        {user && (
          <button className="admin-btn" onClick={() => setScreen("admin")}>
            Admin
          </button>
        )}

        {user && (
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        )}
      </div>
    </header>
  );
}

function StepBar({
  currentScreen,
  setScreen,
  user,
  selectedAddress,
  selectedRestaurant,
  selectedProduct,
}) {
  const steps = [
    { key: "location", label: "Location", enabled: !!user },
    { key: "address", label: "Address", enabled: !!user },
    { key: "restaurants", label: "Restaurants", enabled: !!selectedAddress },
    { key: "menu", label: "Menu", enabled: !!selectedRestaurant },
    { key: "checkout", label: "Checkout", enabled: !!selectedProduct },
  ];

  return (
    <div className="stepbar">
      {steps.map((step, index) => (
        <button
          key={step.key}
          disabled={!step.enabled}
          className={currentScreen === step.key ? "step active-step" : "step"}
          onClick={() => step.enabled && setScreen(step.key)}
        >
          <span>{index + 1}</span>
          {step.label}
        </button>
      ))}
    </div>
  );
}

function LoginPage({ loginForm, setLoginForm, login }) {
  return (
    <main className="login-wrapper">
      <section className="login-card">
        <div className="brand-logo">🍔</div>

        <h2>Login to Mini Swiggy</h2>
        <p>Enter customer details to start ordering food.</p>

        <label>Name</label>
        <input
          value={loginForm.name}
          onChange={(e) =>
            setLoginForm({ ...loginForm, name: e.target.value })
          }
          placeholder="Customer Name"
        />

        <label>Email</label>
        <input
          value={loginForm.email}
          onChange={(e) =>
            setLoginForm({ ...loginForm, email: e.target.value })
          }
          placeholder="Customer Email"
        />

        <label>Membership</label>
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

        <button className="primary-btn full-btn" onClick={login}>
          Login / Register
        </button>
      </section>
    </main>
  );
}

function LocationPage({
  currentLocation,
  locationStatus,
  getCurrentLocation,
  useHyderabadDemoLocation,
  useBangaloreDemoLocation,
  continueToAddress,
}) {
  return (
    <main className="page">
      <section className="page-title">
        <h2>📍 Confirm Current Location</h2>
        <p>This location can be used to create your delivery address.</p>
      </section>

      <section className="location-card">
        <h3>Current Location</h3>

        <div className="location-name">{locationStatus}</div>
        <p className="muted">{currentLocation.locationName}</p>

        <div className="location-grid">
          <div>
            <span>Latitude</span>
            <strong>{currentLocation.latitude}</strong>
          </div>

          <div>
            <span>Longitude</span>
            <strong>{currentLocation.longitude}</strong>
          </div>
        </div>

        <div className="button-row">
          <button className="primary-btn" onClick={getCurrentLocation}>
            Use My Current Location
          </button>

          <button className="outline-btn" onClick={useHyderabadDemoLocation}>
            Hyderabad Demo
          </button>

          <button className="outline-btn" onClick={useBangaloreDemoLocation}>
            Bengaluru Demo
          </button>
        </div>

        <button className="primary-btn full-btn" onClick={continueToAddress}>
          Continue to Address
        </button>
      </section>
    </main>
  );
}

function AddressPage({
  addresses,
  selectedAddress,
  setSelectedAddress,
  addressForm,
  setAddressForm,
  currentLocation,
  saveAddress,
  continueToRestaurants,
}) {
  function setSelfAddress() {
    setAddressForm({
      receiver_name: "Self",
      receiver_phone: "",
      address_label: "Home",
      address_line: currentLocation.locationName || "Current Location",
      area: currentLocation.area || "Current Area",
      city: currentLocation.city || "Hyderabad",
      state: currentLocation.state || "Telangana",
      pincode: "500060",
      latitude: currentLocation.latitude,
      longitude: currentLocation.longitude,
      is_default: 1,
      order_for_someone_else_flag: 0,
      receiver_type: "Self",
    });
  }

  function setFriendAddress() {
    setAddressForm({
      receiver_name: "Friend",
      receiver_phone: "8888888888",
      address_label: "Friend Home",
      address_line: "Friend Home, Gachibowli, Hyderabad",
      area: "Gachibowli",
      city: "Hyderabad",
      state: "Telangana",
      pincode: "500032",
      latitude: 17.4401,
      longitude: 78.3489,
      is_default: 0,
      order_for_someone_else_flag: 1,
      receiver_type: "Friend",
    });
  }

  function setFamilyAddress() {
    setAddressForm({
      receiver_name: "Family Member",
      receiver_phone: "7777777777",
      address_label: "Family Home",
      address_line: "Family Home, Kukatpally, Hyderabad",
      area: "Kukatpally",
      city: "Hyderabad",
      state: "Telangana",
      pincode: "500072",
      latitude: 17.4948,
      longitude: 78.3996,
      is_default: 0,
      order_for_someone_else_flag: 1,
      receiver_type: "Family",
    });
  }

  function setOfficeAddress() {
    setAddressForm({
      receiver_name: "Colleague",
      receiver_phone: "6666666666",
      address_label: "Office",
      address_line: "Office, Hitech City, Hyderabad",
      area: "Hitech City",
      city: "Hyderabad",
      state: "Telangana",
      pincode: "500081",
      latitude: 17.4435,
      longitude: 78.3772,
      is_default: 0,
      order_for_someone_else_flag: 1,
      receiver_type: "Colleague",
    });
  }

  return (
    <main className="page">
      <section className="page-title">
        <h2>🏠 Choose Delivery Address</h2>
        <p>
          Select your own address or place an order for someone else like friend,
          family, or office colleague.
        </p>
      </section>

      <section className="address-mode-grid">
        <div
          className={
            addressForm.receiver_type === "Self"
              ? "address-mode-card active-mode-card"
              : "address-mode-card"
          }
          onClick={setSelfAddress}
        >
          <div className="mode-icon">📍</div>
          <h3>Order for Myself</h3>
          <p>Use my current location or home address.</p>
        </div>

        <div
          className={
            addressForm.receiver_type !== "Self"
              ? "address-mode-card active-mode-card"
              : "address-mode-card"
          }
          onClick={setFriendAddress}
        >
          <div className="mode-icon">🎁</div>
          <h3>Order for Someone Else</h3>
          <p>Send food to friend, family, or office address.</p>
        </div>
      </section>

      <section className="address-layout">
        <div className="checkout-card">
          <div className="section-header-row">
            <div>
              <h3>Saved Addresses</h3>
              <p className="muted">
                Select one saved address before continuing to restaurants.
              </p>
            </div>
          </div>

          {addresses.length === 0 && (
            <div className="empty-state">
              <div>🏠</div>
              <h4>No saved addresses yet</h4>
              <p>Add your first delivery address from the form.</p>
            </div>
          )}

          {addresses.map((address) => (
            <div
              key={address.address_id}
              className={
                selectedAddress?.address_id === address.address_id
                  ? "address-card selected-address"
                  : "address-card"
              }
              onClick={() => setSelectedAddress(address)}
            >
              <div className="address-card-header">
                <h4>
                  {address.address_label} - {address.receiver_name}
                </h4>

                {address.order_for_someone_else_flag === 1 ? (
                  <span className="address-badge other-badge">
                    Someone Else
                  </span>
                ) : (
                  <span className="address-badge self-badge">Self</span>
                )}
              </div>

              <p>{address.address_line}</p>

              <p className="muted">
                {address.area}, {address.city} | {address.receiver_type}
              </p>

              <p className="muted">
                Lat: {address.latitude} | Lon: {address.longitude}
              </p>
            </div>
          ))}

          <button
            className="primary-btn full-btn"
            disabled={!selectedAddress}
            onClick={continueToRestaurants}
          >
            Continue to Restaurants
          </button>
        </div>

        <div className="checkout-card">
          <div className="section-header-row">
            <div>
              <h3>Add Delivery Address</h3>
              <p className="muted">
                Choose quick address or manually edit the address details.
              </p>
            </div>
          </div>

          <div className="quick-address-row">
            <button className="quick-address-btn" onClick={setSelfAddress}>
              📍 Myself
            </button>

            <button className="quick-address-btn" onClick={setFriendAddress}>
              🎁 Friend
            </button>

            <button className="quick-address-btn" onClick={setFamilyAddress}>
              👨‍👩‍👧 Family
            </button>

            <button className="quick-address-btn" onClick={setOfficeAddress}>
              🏢 Office
            </button>
          </div>

          <div className="selected-mode-info">
            {addressForm.order_for_someone_else_flag === 1 ? (
              <>
                <strong>Ordering for someone else</strong>
                <p>
                  Receiver type: {addressForm.receiver_type}. Delivery will go
                  to a different selected address.
                </p>
              </>
            ) : (
              <>
                <strong>Ordering for myself</strong>
                <p>
                  Delivery will use your current/home address as customer
                  location.
                </p>
              </>
            )}
          </div>

          <div className="form-grid">
            <label>
              Receiver Name
              <input
                value={addressForm.receiver_name}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    receiver_name: e.target.value,
                  })
                }
              />
            </label>

            <label>
              Phone
              <input
                value={addressForm.receiver_phone}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    receiver_phone: e.target.value,
                  })
                }
              />
            </label>

            <label>
              Address Label
              <select
                value={addressForm.address_label}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    address_label: e.target.value,
                  })
                }
              >
                <option value="Home">Home</option>
                <option value="Office">Office</option>
                <option value="Friend Home">Friend Home</option>
                <option value="Family Home">Family Home</option>
              </select>
            </label>

            <label>
              Receiver Type
              <select
                value={addressForm.receiver_type}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    receiver_type: e.target.value,
                    order_for_someone_else_flag:
                      e.target.value === "Self" ? 0 : 1,
                  })
                }
              >
                <option value="Self">Self</option>
                <option value="Friend">Friend</option>
                <option value="Family">Family</option>
                <option value="Colleague">Colleague</option>
              </select>
            </label>

            <label className="full-field">
              Address Line
              <input
                value={addressForm.address_line}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    address_line: e.target.value,
                  })
                }
              />
            </label>

            <label>
              Area
              <input
                value={addressForm.area}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    area: e.target.value,
                  })
                }
              />
            </label>

            <label>
              City
              <input
                value={addressForm.city}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    city: e.target.value,
                  })
                }
              />
            </label>

            <label>
              State
              <input
                value={addressForm.state}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    state: e.target.value,
                  })
                }
              />
            </label>

            <label>
              Pincode
              <input
                value={addressForm.pincode}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    pincode: e.target.value,
                  })
                }
              />
            </label>

            <label>
              Latitude
              <input
                type="number"
                value={addressForm.latitude}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    latitude: Number(e.target.value),
                  })
                }
              />
            </label>

            <label>
              Longitude
              <input
                type="number"
                value={addressForm.longitude}
                onChange={(e) =>
                  setAddressForm({
                    ...addressForm,
                    longitude: Number(e.target.value),
                  })
                }
              />
            </label>
          </div>

          <button className="primary-btn full-btn" onClick={saveAddress}>
            Save Address
          </button>
        </div>
      </section>
    </main>
  );
}


function RestaurantsPage({ restaurants, selectedAddress, selectRestaurant }) {
  return (
    <main className="page">
      <section className="page-title">
        <h2>Restaurants Near {selectedAddress?.area || "You"}</h2>
        <p>Distance is calculated from the selected delivery address.</p>
      </section>

      <div className="restaurant-list">
        {restaurants.map((restaurant) => {
          const distance = calcDistanceKm(
            selectedAddress.latitude,
            selectedAddress.longitude,
            restaurant.restaurant_latitude,
            restaurant.restaurant_longitude
          );

          return (
            <div
              key={restaurant.restaurant_id}
              className="restaurant-card"
              onClick={() => selectRestaurant(restaurant)}
            >
              <div className="restaurant-image">
                {cuisineEmoji(restaurant.cuisine_tag)}
              </div>

              <div className="restaurant-info">
                <h3>{restaurant.restaurant_name}</h3>
                <p>
                  {restaurant.cuisine_tag} • {restaurant.location_name}
                </p>
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
        })}
      </div>
    </main>
  );
}

function MenuPage({
  selectedRestaurant,
  products,
  selectProduct,
  backToRestaurants,
}) {
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
            <div key={product.product_id} className="food-card">
              <div>
                <span
                  className={
                    product.food_type === "Veg" ? "veg-dot" : "nonveg-dot"
                  }
                />
                <h4>{product.product_name}</h4>
                <p>₹{product.price}</p>
                <p className="muted">{product.description}</p>
              </div>

              <div className="food-action">
                <div className="food-image">
                  {cuisineEmoji(product.cuisine_tag)}
                </div>

                <button className="add-btn" onClick={() => selectProduct(product)}>
                  ADD
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function CheckoutPage({
  selectedRestaurant,
  selectedProduct,
  selectedAddress,
  checkout,
  setCheckout,
  placeOrder,
  backToMenu,
}) {
  const grossAmount = selectedProduct.price * checkout.quantity;

  const totalDiscount =
    checkout.coupon_discount_amount + checkout.membership_benefit_amount;

  const netAmount = grossAmount - totalDiscount;

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
            {selectedAddress.area}, {selectedAddress.city} |{" "}
            {selectedAddress.receiver_type}
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
                  setCheckout({
                    ...checkout,
                    coupon_used_num: Number(e.target.value),
                  })
                }
              >
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </label>
          </div>
        </div>
      </section>

      <aside className="bill-card">
        <h3>Cart</h3>

        <div className="cart-item">
          <div>
            <h4>{selectedProduct.product_name}</h4>
            <p>{selectedRestaurant.restaurant_name}</p>
          </div>

          <strong>₹{selectedProduct.price}</strong>
        </div>

        <div className="bill-row">
          <span>Quantity</span>
          <span>{checkout.quantity}</span>
        </div>

        <div className="bill-row">
          <span>Gross Amount</span>
          <span>₹{grossAmount}</span>
        </div>

        <div className="bill-row discount">
          <span>Coupon Discount</span>
          <span>-₹{checkout.coupon_discount_amount}</span>
        </div>

        <div className="bill-row discount">
          <span>Membership Benefit</span>
          <span>-₹{checkout.membership_benefit_amount}</span>
        </div>

        <div className="bill-row total">
          <span>To Pay</span>
          <span>₹{netAmount}</span>
        </div>

        <p className="muted">
          Weather, distance and model v2 delay risk will be checked after placing
          order.
        </p>

        <button className="primary-btn full-btn" onClick={placeOrder}>
          Place Order
        </button>
      </aside>
    </main>
  );
}

function OrderSuccessPage({ orderResult, startAgain, viewAdmin }) {
  return (
    <main className="page">
      <section className="success-card">
        <div className="success-icon">✅</div>

        <h2>Order Placed Successfully</h2>

        <p>
          Order #{orderResult.order_id} from {orderResult.restaurant_name}
        </p>

        <h3
          className={
            orderResult.delay_risk === "High Delay Risk"
              ? "risk-high"
              : "risk-low"
          }
        >
          {orderResult.delay_risk} | Probability:{" "}
          {Number(orderResult.delay_probability || 0).toFixed(2)}
        </h3>

        <div className="insight-grid">
          <div>
            <span>Receiver</span>
            <strong>{orderResult.receiver_name}</strong>
          </div>

          <div>
            <span>Address Type</span>
            <strong>{orderResult.receiver_type}</strong>
          </div>

          <div>
            <span>Customer Area</span>
            <strong>{orderResult.customer_area}</strong>
          </div>

          <div>
            <span>Restaurant Area</span>
            <strong>{orderResult.restaurant_area}</strong>
          </div>

          <div>
            <span>Distance</span>
            <strong>{orderResult.distance_km} km</strong>
          </div>

          <div>
            <span>ETA</span>
            <strong>{orderResult.estimated_travel_minutes} mins</strong>
          </div>

          <div>
            <span>Weather</span>
            <strong>{orderResult.weather}</strong>
          </div>

          <div>
            <span>Rain Flag</span>
            <strong>{orderResult.raining_num}</strong>
          </div>

          <div>
            <span>Scenario</span>
            <strong>{orderResult.operational_scenario}</strong>
          </div>

          <div>
            <span>Model</span>
            <strong>{orderResult.model_version}</strong>
          </div>
        </div>

        <div className="recommendation">
          <strong>Recommendation:</strong> {orderResult.recommendation}
        </div>

        <div className="button-row center">
          <button className="primary-btn" onClick={startAgain}>
            Order More
          </button>

          <button className="outline-btn" onClick={viewAdmin}>
            View Admin Dashboard
          </button>
        </div>
      </section>
    </main>
  );
}

function AdminPage({ adminOrders, back }) {
  return (
    <main className="page">
      <button className="text-btn" onClick={back}>
        ← Back to restaurants
      </button>

      <section className="page-title">
        <h2>Admin - Live Orders & ML Predictions</h2>
        <p>Orders with weather, distance, scenario and model v2 prediction.</p>
      </section>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>User</th>
              <th>Receiver</th>
              <th>Type</th>
              <th>Customer Area</th>
              <th>Restaurant</th>
              <th>Distance</th>
              <th>Weather</th>
              <th>Scenario</th>
              <th>Risk</th>
              <th>Probability</th>
            </tr>
          </thead>

          <tbody>
            {adminOrders.map((order) => (
              <tr key={order.order_id}>
                <td>{order.order_id}</td>
                <td>{order.user_id}</td>
                <td>{order.receiver_name}</td>
                <td>{order.receiver_type}</td>
                <td>{order.customer_area}</td>
                <td>{order.restaurant_location_name}</td>
                <td>{order.distance_km} km</td>
                <td>{order.weather_condition}</td>
                <td>{order.operational_scenario}</td>
                <td>{order.delay_risk}</td>
                <td>
                  {order.delay_probability
                    ? Number(order.delay_probability).toFixed(2)
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}

export default App;