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
          {orderResult.delay_probability.toFixed(2)}
        </h3>

        <div className="insight-grid">
          <div>
            <span>Receiver</span>
            <strong>{orderResult.receiver_name}</strong>
          </div>

          <div>
            <span>Delivery Address Type</span>
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
            View Admin
          </button>
        </div>
      </section>
    </main>
  );
}

export default OrderSuccessPage;