from math import radians, degrees, sin, cos, atan2, sqrt

def calculate_azimuth(coord1, coord2):
    """Azimuth (initial bearing) in degrees from coord1 to coord2."""
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    azimuth = atan2(x, y)
    return (degrees(azimuth) + 360) % 360

def calculate_elevation_angle(coord1, alt1, coord2, alt2):
    """Elevation angle in degrees from point 1 to point 2."""
    horizontal_distance = haversine_distance(coord1, coord2)
    vertical_diff = alt2 - alt1
    elevation = atan2(vertical_diff, horizontal_distance)
    return degrees(elevation)

def haversine_distance(coord1, coord2):
    """Surface distance between two lat/lon coordinates in meters."""
    R = 6371000  # Earth radius in meters
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Example usage
if __name__ == "__main__":
    pos1 = (59.577698, 19.257585, 86)  # Notodden
    # pos2 = (-18.86361400868, 70.382275490587, 421997.09937094)   # ISS

    # pos1 = (59.9111, 10.7528, 100)  # Oslo
    # pos2 = (60.3913, 5.3221, 100)   # Bergen

    pos2 = (40.7128, -74.0060, 100)

    coord1 = (pos1[0], pos1[1])
    coord2 = (pos2[0], pos2[1])

    azimuth = calculate_azimuth(coord1, coord2)
    elevation = calculate_elevation_angle(coord1, pos1[2], coord2, pos2[2])

    print(f"Azimuth (horizontal): {azimuth:.2f}°")
    print(f"Elevation (vertical): {elevation:.2f}°")