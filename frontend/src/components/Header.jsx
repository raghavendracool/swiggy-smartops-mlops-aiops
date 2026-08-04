function Header({ user, setScreen, logout }) {
  return (
    <header className="top-header">
      <div className="brand-section" onClick={() => setScreen("location")}>
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

export default Header;