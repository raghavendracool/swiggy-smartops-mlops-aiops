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

export default LocationPage;