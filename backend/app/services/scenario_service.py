def evaluate_order_business_scenario(
    delay_probability,
    delay_risk,
    distance_km,
    raining_num,
    surge_num,
    net_amount,
    order_for_someone_else_flag,
    weather_api_status,
    operational_scenario,
    estimated_travel_minutes=0,
):
    delay_probability = float(delay_probability or 0)
    distance_km = float(distance_km or 0)
    estimated_travel_minutes = float(estimated_travel_minutes or 0)
    net_amount = float(net_amount or 0)
    raining_num = int(raining_num or 0)
    surge_num = int(surge_num or 0)
    order_for_someone_else_flag = int(order_for_someone_else_flag or 0)

    if (
        distance_km <= 2
        and estimated_travel_minutes <= 10
        and raining_num == 0
        and surge_num == 0
        and delay_probability < 0.75
    ):
        if order_for_someone_else_flag == 1:
            return {
                "priority_level": "Medium",
                "business_scenario": "Nearby Someone Else Order",
                "business_reason": "Restaurant is nearby and ETA is low, but this order is for someone else, so address accuracy and communication still matter.",
                "business_action": "Show clear ETA to sender and verify delivery address.",
                "business_impact": "Improves trust for friend, family, and office delivery orders.",
            }

        return {
            "priority_level": "Low",
            "business_scenario": "Nearby Low ETA Order",
            "business_reason": "Restaurant is nearby, ETA is low, and there is no rain or surge impact.",
            "business_action": "Continue normal dispatch.",
            "business_impact": "Avoids unnecessary operational escalation.",
        }

    if weather_api_status != "success":
        return {
            "priority_level": "Warning",
            "business_scenario": "Weather API Failed Fallback",
            "business_reason": "Weather API failed, so fallback rain input was used for prediction.",
            "business_action": "Monitor this order manually and retry weather lookup if needed.",
            "business_impact": "Prevents blind prediction when external weather signal is unavailable.",
        }

    if delay_probability >= 0.85:
        return {
            "priority_level": "Critical",
            "business_scenario": "Very High Delay Probability",
            "business_reason": "The ML model predicted very high probability of delivery delay.",
            "business_action": "Assign delivery partner early, show realistic ETA, and alert city operations.",
            "business_impact": "Reduces customer complaints, cancellations, refunds, and bad delivery experience.",
        }

    if raining_num == 1 and distance_km > 8 and surge_num == 1:
        return {
            "priority_level": "Critical",
            "business_scenario": "Rain + Long Distance + Surge",
            "business_reason": "Rain, long distance, and surge together increase delivery delay risk.",
            "business_action": "Increase delivery partner availability and monitor this delivery zone.",
            "business_impact": "Improves rainy-day operations and protects customer experience.",
        }

    if delay_risk == "High Delay Risk" and net_amount >= 1000:
        return {
            "priority_level": "High",
            "business_scenario": "High Value Order + High Delay Risk",
            "business_reason": "This is a high-value order with high delay probability.",
            "business_action": "Prioritize order handling and avoid late delivery for premium revenue protection.",
            "business_impact": "Protects revenue and reduces risk of losing high-value customers.",
        }

    if order_for_someone_else_flag == 1 and delay_risk == "High Delay Risk":
        return {
            "priority_level": "High",
            "business_scenario": "Someone Else Order + High Delay Risk",
            "business_reason": "The order is being sent to someone else, so a bad delivery experience can affect both sender and receiver.",
            "business_action": "Improve ETA communication and monitor delivery route carefully.",
            "business_impact": "Improves trust for gift, family, friend, and office delivery use cases.",
        }

    if raining_num == 1 and distance_km <= 3:
        return {
            "priority_level": "Medium",
            "business_scenario": "Rain + Nearby Order",
            "business_reason": "Rain is detected, but the restaurant is near the customer.",
            "business_action": "Use rain-aware ETA and continue normal dispatch.",
            "business_impact": "Maintains ETA accuracy without over-allocating delivery partners.",
        }

    if raining_num == 0 and distance_km > 8:
        return {
            "priority_level": "Medium",
            "business_scenario": "Non-rain + Long Distance",
            "business_reason": "Weather is normal, but customer and restaurant distance is high.",
            "business_action": "Show realistic ETA and assign partner based on distance.",
            "business_impact": "Prevents customer dissatisfaction from underestimated delivery time.",
        }

    if surge_num == 1 and distance_km > 7:
        return {
            "priority_level": "Medium",
            "business_scenario": "Surge + Medium/Far Distance",
            "business_reason": "Demand surge and distance may impact delivery time.",
            "business_action": "Monitor local delivery partner capacity.",
            "business_impact": "Improves delivery partner planning during peak demand.",
        }

    if order_for_someone_else_flag == 1:
        return {
            "priority_level": "Medium",
            "business_scenario": "Order For Someone Else",
            "business_reason": "Delivery address is different from the customer's current/default location.",
            "business_action": "Validate address quality and show clear ETA to sender.",
            "business_impact": "Improves success rate for family, friend, and office orders.",
        }

    return {
        "priority_level": "Low",
        "business_scenario": operational_scenario or "Normal Order",
        "business_reason": "No major operational risk pattern detected.",
        "business_action": "Continue normal order monitoring.",
        "business_impact": "Maintains stable delivery operations.",
    }