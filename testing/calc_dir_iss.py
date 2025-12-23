import requests
from math import sin, cos, atan2, sqrt, radians, degrees

# WGS84 constants
a = 6378137.0
f = 1 / 298.257223563
e_sq = f * (2 - f)

def geodetic_to_ecef(lat, lon, alt):
    lat, lon = radians(lat), radians(lon)
    N = a / sqrt(1 - e_sq * sin(lat)**2)
    x = (N + alt) * cos(lat) * cos(lon)
    y = (N + alt) * cos(lat) * sin(lon)
    z = (N * (1 - e_sq) + alt) * sin(lat)
    return x, y, z

def ecef_to_enu(x, y, z, lat_ref, lon_ref, alt_ref):
    x0, y0, z0 = geodetic_to_ecef(lat_ref, lon_ref, alt_ref)
    dx, dy, dz = x - x0, y - y0, z - z0

    lat_ref = radians(lat_ref)
    lon_ref = radians(lon_ref)

    t = [
        [-sin(lon_ref),              cos(lon_ref),              0],
        [-sin(lat_ref)*cos(lon_ref), -sin(lat_ref)*sin(lon_ref), cos(lat_ref)],
        [ cos(lat_ref)*cos(lon_ref),  cos(lat_ref)*sin(lon_ref), sin(lat_ref)],
    ]

    east  = t[0][0]*dx + t[0][1]*dy + t[0][2]*dz
    north = t[1][0]*dx + t[1][1]*dy + t[1][2]*dz
    up    = t[2][0]*dx + t[2][1]*dy + t[2][2]*dz

    return east, north, up

def calculate_azimuth_elevation(observer, target):
    lat1, lon1, alt1 = observer
    lat2, lon2, alt2 = target

    x, y, z = geodetic_to_ecef(lat2, lon2, alt2)
    e, n, u = ecef_to_enu(x, y, z, lat1, lon1, alt1)

    azimuth = atan2(e, n)
    elevation = atan2(u, sqrt(e**2 + n**2))

    return (degrees(azimuth) + 360) % 360, degrees(elevation)

def haversine_distance(coord1, coord2):
    R = 6371000
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def euclidean_distance(p1, p2):
    return sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))

def get_position_from_api(url):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return (data["latitude"], data["longitude"], data["altitude"] * 1000)  # km → meters

# --- Example usage ---

if __name__ == "__main__":
    # Replace this with your actual API URL:
    api_url = "https://api.wheretheiss.at/v1/satellites/25544"

    # Observer location
    observer = (59.9111, 10.7528, 50)  # (lat, lon, alt in meters)

    try:
        target = get_position_from_api(api_url)

        # Distance calculations
        surface_dist = haversine_distance(observer[:2], target[:2])
        dist_3d = euclidean_distance(geodetic_to_ecef(*observer), geodetic_to_ecef(*target))
        azimuth, elevation = calculate_azimuth_elevation(observer, target)

        print(f"Target location: lat={target[0]:.4f}, lon={target[1]:.4f}, alt={target[2]/1000:.2f} km")
        print(f"Surface distance:       {surface_dist/1000:.2f} km")
        print(f"3D straight-line dist:  {dist_3d/1000:.2f} km")
        print(f"Azimuth (bearing):      {azimuth:.2f}°")
        print(f"Elevation angle:        {elevation:.2f}°")

    except Exception as e:
        print(f"Failed to fetch or process data: {e}")
