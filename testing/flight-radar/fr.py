from FlightRadar24 import FlightRadar24API
fr_api = FlightRadar24API()

# bounds = fr_api.get_bounds_by_point(59.891338, 10.8463307, 2000) // Oppsal
bounds = fr_api.get_bounds_by_point(60.1951575, 11.0701408, 10000)
flights = fr_api.get_flights(bounds = bounds)
print(f"Number of flights in area: {len(flights)}")

# print(flights[0].__dict__)

for flight in flights:
    # print(f"Flight: {flight.callsign}, From: {flight.origin}, To: {flight.destination}")
    print(flight)