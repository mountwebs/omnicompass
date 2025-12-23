from math import radians, cos, sin, sqrt

def geodetic_to_ecef(lat, lon, alt):
    """Convert geodetic coordinates to ECEF (Earth-Centered, Earth-Fixed) XYZ."""
    # WGS84 ellipsoid constants
    a = 6378137  # semi-major axis in meters
    e2 = 6.69437999014e-3  # square of eccentricity

    lat_rad = radians(lat)
    lon_rad = radians(lon)

    N = a / sqrt(1 - e2 * sin(lat_rad)**2)

    x = (N + alt) * cos(lat_rad) * cos(lon_rad)
    y = (N + alt) * cos(lat_rad) * sin(lon_rad)
    z = (N * (1 - e2) + alt) * sin(lat_rad)

    return x, y, z

def direction_vector_ecef(pos1, pos2):
    x1, y1, z1 = geodetic_to_ecef(*pos1)
    x2, y2, z2 = geodetic_to_ecef(*pos2)

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    mag = sqrt(dx**2 + dy**2 + dz**2)
    return dx / mag, dy / mag, dz / mag  # unit vector

# Example usage
pos1 = (59.9111, 10.7528, 100)
pos2 = (60.3913, 5.3221, 300)

dir_vector = direction_vector_ecef(pos1, pos2)
print(f"3D unit direction vector: {dir_vector}")