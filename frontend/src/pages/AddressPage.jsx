function AddressPage({
  addresses,
  selectedAddress,
  setSelectedAddress,
  addressForm,
  setAddressForm,
  saveAddress,
  continueToRestaurants,
}) {
  return (
    <main className="page">
      <section className="page-title">
        <h2>🏠 Delivery Address</h2>
        <p>Select your address or add address for someone else.</p>
      </section>

      <section className="address-layout">
        <div className="checkout-card">
          <h3>Saved Addresses</h3>

          {addresses.length === 0 && (
            <p className="muted">No saved addresses yet. Add one below.</p>
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
              <h4>{address.address_label} - {address.receiver_name}</h4>
              <p>{address.address_line}</p>
              <p className="muted">
                {address.area}, {address.city} | {address.receiver_type}
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
          <h3>Add / Update Address</h3>

          <div className="form-grid">
            <label>
              Receiver Name
              <input
                value={addressForm.receiver_name}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, receiver_name: e.target.value })
                }
              />
            </label>

            <label>
              Phone
              <input
                value={addressForm.receiver_phone}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, receiver_phone: e.target.value })
                }
              />
            </label>

            <label>
              Address Label
              <select
                value={addressForm.address_label}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, address_label: e.target.value })
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

            <label>
              Address Line
              <input
                value={addressForm.address_line}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, address_line: e.target.value })
                }
              />
            </label>

            <label>
              Area
              <input
                value={addressForm.area}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, area: e.target.value })
                }
              />
            </label>

            <label>
              City
              <input
                value={addressForm.city}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, city: e.target.value })
                }
              />
            </label>

            <label>
              Pincode
              <input
                value={addressForm.pincode}
                onChange={(e) =>
                  setAddressForm({ ...addressForm, pincode: e.target.value })
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

export default AddressPage;