from skyfield.api import Loader
import os

def download_ephemeris():
    data_dir = os.path.join(os.path.dirname(__file__), '../src/domain/data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"Downloading de421.bsp to {data_dir}...")
    load = Loader(data_dir)
    load('de421.bsp')
    print("Download complete.")

if __name__ == "__main__":
    download_ephemeris()
