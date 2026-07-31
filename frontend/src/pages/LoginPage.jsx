function LoginPage({ loginForm, setLoginForm, login }) {
  return (
    <main className="login-wrapper">
      <section className="login-card">
        <div className="brand-logo">🍔</div>

        <h2>Login to Mini Swiggy</h2>
        <p>Enter customer details to start ordering.</p>

        <label>Name</label>
        <input
          value={loginForm.name}
          onChange={(e) => setLoginForm({ ...loginForm, name: e.target.value })}
        />

        <label>Email</label>
        <input
          value={loginForm.email}
          onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
        />

        <label>Membership</label>
        <select
          value={loginForm.membership_tier}
          onChange={(e) =>
            setLoginForm({ ...loginForm, membership_tier: e.target.value })
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

export default LoginPage;