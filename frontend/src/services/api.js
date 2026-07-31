const API_BASE = "http://127.0.0.1:8000";

export async function apiRequest(path, options = {}) {
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

export function loginUser(payload) {
  return apiRequest("/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function reverseLocation(latitude, longitude) {
  return apiRequest(`/location/reverse?latitude=${latitude}&longitude=${longitude}`);
}

export function getRestaurants() {
  return apiRequest("/restaurants");
}

export function getProducts(restaurantId) {
  return apiRequest(`/restaurants/${restaurantId}/products`);
}

export function createAddress(payload) {
  return apiRequest("/addresses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getUserAddresses(userId) {
  return apiRequest(`/addresses/user/${userId}`);
}

export function placeOrder(payload) {
  return apiRequest("/orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAdminOrders() {
  return apiRequest("/admin/orders");
}