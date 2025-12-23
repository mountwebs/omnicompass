from skyfield.api import Topos, load
from datetime import datetime

# Load planetary data
planets = load('de421.bsp')  # ephemeris file for planetary positions
earth, sun = planets['earth'], planets['sun']

# Load time scale
ts = load.timescale()
t = ts.now()  # or use a specific time: ts.utc(2025, 5, 23, 12, 0)
# t = ts.utc(2025, 12, 21, 21, 34)

# Define observer's location (Oslo, Norway)
observer = earth + Topos(latitude_degrees=59.9111, longitude_degrees=10.7528, elevation_m=50)

# Sun position from observer
sun_apparent = observer.at(t).observe(sun).apparent()
alt, az, distance = sun_apparent.altaz()

# Print results
print(f"Azimuth: {az.degrees:.2f}°")
print(f"Elevation: {alt.degrees:.2f}°")
print(f"Distance: {distance.km:.0f} km")
