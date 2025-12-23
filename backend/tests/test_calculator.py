import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from domain.calculator import CelestialCalculator
from domain.models import ObserverLocation, CelestialBody

def test_calculator_initialization():
    calc = CelestialCalculator()
    assert calc.planets is not None

def test_calculate_sun_position():
    calc = CelestialCalculator()
    # Oslo
    location = ObserverLocation(latitude=59.91, longitude=10.75, elevation=0)
    update = calc.calculate_position(location, CelestialBody.SUN)
    
    assert update.target_id == "SUN"
    assert isinstance(update.azimuth, float)
    assert isinstance(update.altitude, float)
    assert 0 <= update.azimuth <= 360
    assert -90 <= update.altitude <= 90

def test_calculate_mars_position():
    calc = CelestialCalculator()
    location = ObserverLocation(latitude=59.91, longitude=10.75, elevation=0)
    update = calc.calculate_position(location, CelestialBody.MARS)
    
    assert update.target_id == "MARS"
    assert isinstance(update.azimuth, float)
