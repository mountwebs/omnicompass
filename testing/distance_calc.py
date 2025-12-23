from math import radians, degrees, sin, cos, sqrt, atan2
from geopy.distance import geodesic

def haversine_distance(coord1, coord2):
    """Surface distance between two (lat, lon) coordinates using the Haversine formula."""
    R = 6371000  # Earth radius in meters
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def calculate_initial_bearing(coord1, coord2):
    """Initial bearing from coord1 to coord2."""
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlon = lon2 - lon1

    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(dlon))

    bearing = atan2(x, y)
    return (degrees(bearing) + 360) % 360  # Normalize to 0–360°

def calculate_3d_distance(coord1, alt1, coord2, alt2):
    """3D distance between two points including altitude difference."""
    surface_dist = haversine_distance(coord1, coord2)
    alt_diff = alt2 - alt1
    return sqrt(surface_dist**2 + alt_diff**2)

# Example usage
if __name__ == "__main__":
    # print("Distance Calculation Example")
    # Position format: (latitude, longitude, altitude in meters)
    pos1 = (59.577698, 19.257585, 86)  # Notodden
    pos2 = (-18.86361400868, 70.382275490587, 421997.09937094)   # ISS

    coord1 = (pos1[0], pos1[1])
    coord2 = (pos2[0], pos2[1])
    alt1, alt2 = pos1[2], pos2[2]

    surface_dist = haversine_distance(coord1, coord2)
    bearing = calculate_initial_bearing(coord1, coord2)
    dist_3d = calculate_3d_distance(coord1, alt1, coord2, alt2)

    print(f"Surface distance: {surface_dist:.2f} meters")
    print(f"Initial bearing: {bearing:.2f} degrees")
    print(f"3D distance: {dist_3d:.2f} meters")
