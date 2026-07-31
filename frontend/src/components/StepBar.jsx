function StepBar({ screen, setScreen, user, selectedAddress, selectedRestaurant, selectedProduct }) {
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
          className={screen === step.key ? "step active-step" : "step"}
          onClick={() => step.enabled && setScreen(step.key)}
        >
          <span>{index + 1}</span>
          {step.label}
        </button>
      ))}
    </div>
  );
}

export default StepBar;