from skyfield.api import Loader, Topos
from .models import ObserverLocation, DirectionUpdate, CelestialBody
import os

class CelestialCalculator:
    def __init__(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        load = Loader(data_dir)
        self.planets = load('de421.bsp')
        self.ts = load.timescale()
        self.earth = self.planets['earth']
        self.sun = self.planets['sun']
        self.mars = self.planets['mars']
        self.venus = self.planets['venus']
        self.saturn = self.planets['saturn barycenter']
        self.jupiter = self.planets['jupiter barycenter']

    def calculate_position(self, location: ObserverLocation, target: CelestialBody) -> DirectionUpdate:
        t = self.ts.now()
        observer = self.earth + Topos(latitude_degrees=location.latitude, 
                                      longitude_degrees=location.longitude, 
                                      elevation_m=location.elevation)
        
        if target == CelestialBody.SUN:
            target_body = self.sun
        elif target == CelestialBody.MARS:
            target_body = self.mars
        elif target == CelestialBody.VENUS:
            target_body = self.venus
        elif target == CelestialBody.SATURN:
            target_body = self.saturn
        elif target == CelestialBody.JUPITER:
            target_body = self.jupiter
        else:
            # Fallback or error, but for now default to Sun
            target_body = self.sun
        
        apparent = observer.at(t).observe(target_body).apparent()
        alt, az, distance = apparent.altaz()
        
        return DirectionUpdate(
            target_id=target.value,
            azimuth=az.degrees,
            altitude=alt.degrees,
            distance_km=distance.km,
            timestamp=t.utc_datetime()
        )
