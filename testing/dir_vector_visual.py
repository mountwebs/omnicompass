import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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

def plot_3d_vector(pos1_ecef, direction_vector, length=1_000_000):
    """Plot a 3D vector starting at pos1, extending in the direction_vector."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Origin point
    x0, y0, z0 = pos1_ecef
    dx, dy, dz = [v * length for v in direction_vector]

    ax.quiver(x0, y0, z0, dx, dy, dz, color='r', arrow_length_ratio=0.05)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Direction Vector from pos1 to pos2')

    # Auto scale
    ax.auto_scale_xyz([x0, x0 + dx], [y0, y0 + dy], [z0, z0 + dz])
    plt.show()

# Assuming you've already calculated:
# pos1 = (lat, lon, alt)
# pos2 = (lat, lon, alt)
# pos1_ecef = geodetic_to_ecef(*pos1)
# direction = direction_vector_ecef(pos1, pos2)

# pos1 = (59.9111, 10.7528, 100)  # Oslo
# pos2 = (60.3913, 5.3221, 100)   # Bergen
pos1 = (59.577698, 19.257585, 86)  # Notodden
pos2 = (-18.86361400868, 70.382275490587, 421997.09937094)   # ISS
pos1_ecef = geodetic_to_ecef(*pos1)
direction = direction_vector_ecef(pos1, pos2)

plot_3d_vector(pos1_ecef, direction)
