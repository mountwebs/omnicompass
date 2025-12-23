from math import sin, cos, atan2, sqrt, radians, degrees

# WGS84 ellipsoid constants
a = 6378137.0        # major axis
f = 1 / 298.257223563
b = a * (1 - f)      # minor axis
e_sq = f * (2 - f)   # eccentricity squared

def geodetic_to_ecef(lat, lon, alt):
    lat, lon = radians(lat), radians(lon)
    N = a / sqrt(1 - e_sq * sin(lat)**2)
    x = (N + alt) * cos(lat) * cos(lon)
    y = (N + alt) * cos(lat) * sin(lon)
    z = (N * (1 - e_sq) + alt) * sin(lat)
    return x, y, z

def ecef_to_enu(x, y, z, lat_ref, lon_ref, alt_ref):
    x0, y0, z0 = geodetic_to_ecef(lat_ref, lon_ref, alt_ref)

    dx = x - x0
    dy = y - y0
    dz = z - z0

    lat_ref = radians(lat_ref)
    lon_ref = radians(lon_ref)

    t = [
        [-sin(lon_ref),             cos(lon_ref),              0],
        [-sin(lat_ref)*cos(lon_ref), -sin(lat_ref)*sin(lon_ref), cos(lat_ref)],
        [ cos(lat_ref)*cos(lon_ref),  cos(lat_ref)*sin(lon_ref), sin(lat_ref)],
    ]

    east  = t[0][0]*dx + t[0][1]*dy + t[0][2]*dz
    north = t[1][0]*dx + t[1][1]*dy + t[1][2]*dz
    up    = t[2][0]*dx + t[2][1]*dy + t[2][2]*dz

    return east, north, up

def calculate_azimuth_and_elevation(observer, target):
    lat1, lon1, alt1 = observer
    lat2, lon2, alt2 = target

    x, y, z = geodetic_to_ecef(lat2, lon2, alt2)
    e, n, u = ecef_to_enu(x, y, z, lat1, lon1, alt1)

    azimuth = atan2(e, n)
    elevation = atan2(u, sqrt(e**2 + n**2))

    return (degrees(azimuth) + 360) % 360, degrees(elevation)

# Example usage
if __name__ == "__main__":
    pos1 = (59.577698, 19.257585, 86)  # Notodden

    # pos1 = (59.9111, 10.7528, 50)         # oslo
    # pos2 = (40.7128, -74.0060, 10)       # new york
    # pos2 = (60.3913, 5.3221, 86)   # Bergen
    # pos2 = (59.577698, 19.257585, 86)  # Notodden
    pos2 = (-18.86361400868, 70.382275490587, 421997.09937094)   # ISS



    az, el = calculate_azimuth_and_elevation(pos1, pos2)
    print(f"Azimuth: {az:.2f}°")
    print(f"Elevation: {el:.2f}°")