function AdminPage({ adminOrders, back }) {
  return (
    <main className="page">
      <button className="text-btn" onClick={back}>
        ← Back
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
              <th>Address Type</th>
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
                    ? order.delay_probability.toFixed(2)
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

export default AdminPage;