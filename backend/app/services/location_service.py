import requests


def reverse_geocode_location(latitude, longitude):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "zoom": 14,
            "addressdetails": 1,
        }

        headers = {
            "User-Agent": "swiggy-smartops-demo-app"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()
        address = data.get("address", {})

        area = (
            address.get("suburb")
            or address.get("neighbourhood")
            or address.get("quarter")
            or address.get("road")
            or address.get("city_district")
            or address.get("county")
            or "Current Area"
        )

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("state_district")
            or "Current City"
        )

        state = address.get("state", "Unknown State")

        display_name = data.get(
            "display_name",
            f"{area}, {city}, {state}"
        )

        return {
            "area": area,
            "city": city,
            "state": state,
            "display_name": display_name,
            "status": "success",
        }

    except Exception as e:
        return {
            "area": "Current Area",
            "city": "Current City",
            "state": "Unknown State",
            "display_name": f"Location lookup failed: {str(e)}",
            "status": "failed",
        }