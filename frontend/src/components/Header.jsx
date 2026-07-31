function Header({ user, setScreen, logout }) {
  return (
    <header className="top-header">
      <div>
        <h1>Swiggy SmartOps</h1>
        <p>Food app with weather, distance and ML delay prediction</p>
      </div>

      <div className="header-actions">
        {user && <span className="user-chip">👤 {user.name}</span>}

        {user && (
          <button className="outline-btn" onClick={() => setScreen("admin")}>
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