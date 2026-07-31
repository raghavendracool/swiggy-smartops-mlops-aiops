from math import atan2, cos, radians, sin, sqrt


def haversine_distance_km(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0

    lat1_rad = radians(float(lat1))
    lon1_rad = radians(float(lon1))
    lat2_rad = radians(float(lat2))
    lon2_rad = radians(float(lon2))

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(earth_radius_km * c, 2)


def get_distance_bucket(distance_km):
    if distance_km <= 3:
        return "Near"

    if distance_km <= 7:
        return "Medium"

    if distance_km <= 12:
        return "Far"

    return "Very Far"


def estimate_travel_minutes(distance_km, raining_num, surge_num):
    if distance_km <= 0:
        return 0

    average_speed_kmph = 22

    minutes = (distance_km / average_speed_kmph) * 60

    if raining_num == 1:
        minutes = minutes * 1.20

    if surge_num == 1:
        minutes = minutes * 1.10

    return round(minutes, 2)