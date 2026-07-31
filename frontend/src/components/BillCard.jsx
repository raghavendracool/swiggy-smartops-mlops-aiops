function BillCard({ selectedRestaurant, selectedProduct, checkout, placeOrder }) {
  const grossAmount = selectedProduct.price * checkout.quantity;

  const totalDiscount =
    checkout.coupon_discount_amount + checkout.membership_benefit_amount;

  const netAmount = grossAmount - totalDiscount;

  return (
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
        Weather and delay risk will be checked after placing the order.
      </p>

      <button className="primary-btn full-btn" onClick={placeOrder}>
        Place Order
      </button>
    </aside>
  );
}

export default BillCard;