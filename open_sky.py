import requests


# 3.645888,57.688398,13.225966,61.477179

params = {
    'lamin': '3.645888',
    'lomin': '57.688398',
    'lamax': '13.225966',
    'lomax': '61.477179',
    'extended': 1
}

r = requests.get('https://opensky-network.org/api/states/all', params=params)

print(r.json());