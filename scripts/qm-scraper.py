import requests
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import time

# Target parameters (adjust x, y to target a specific boundary region)
zoom = 9
x_range = range(300, 302)  # Just 2x2 tiles for testing
y_range = range(90, 92)

# Endpoints
url_albedo = "https://lroc-tiles.quickmap.io/tiles/lola_albedo/lunar-fulleqc/{zoom}/{x}/{y}.flt?size=256"
url_dtm = "https://lroc-tiles.quickmap.io/tiles/qts_demstack/lunar-fulleqc/{zoom}/{x}/{y}.flt?size=256"
url_mask = "https://lroc-tiles.quickmap.io/tiles/lmare_boundaries/lunar-fulleqc/{zoom}/{x}/{y}.png"

master_df = pd.DataFrame()

for x in x_range:
    for y in y_range:
        print(f"Processing tile {zoom}/{x}/{y}...")
        try:
            # 1. Fetch raw floating-point Albedo data
            r_albedo = requests.get(url_albedo.format(zoom=zoom, x=x, y=y), timeout=10)
            if r_albedo.status_code != 200: continue
            # Decode bytes directly into a 1D float32 numpy array
            albedo_arr = np.frombuffer(r_albedo.content, dtype=np.float32)

            # 2. Fetch raw floating-point Elevation data
            r_dtm = requests.get(url_dtm.format(zoom=zoom, x=x, y=y), timeout=10)
            if r_dtm.status_code != 200: continue
            dtm_arr = np.frombuffer(r_dtm.content, dtype=np.float32)

            # 3. Fetch the Mare Boundaries (PNG)
            r_mask = requests.get(url_mask.format(zoom=zoom, x=x, y=y), timeout=10)
            if r_mask.status_code == 200:
                # Read image, convert to RGBA to check transparency (alpha channel)
                img = Image.open(BytesIO(r_mask.content)).convert("RGBA")
                # If the pixel is not completely transparent, assume it is Mare
                alpha_channel = np.array(img)[:, :, 3].flatten()
                labels = np.where(alpha_channel > 0, 1, 2) # 1: Mare, 2: Highland
            else:
                # If no boundary tile exists, assume it's entirely Highland
                labels = np.full(256 * 256, 2)

            # 4. Append to our master dataset
            tile_df = pd.DataFrame({
                'Albedo': albedo_arr,
                'Elevation': dtm_arr,
                'Class': labels
            })

            # Filter out any "No Data" values (often represented as extreme negatives like -9999)
            tile_df = tile_df[(tile_df['Albedo'] > -100) & (tile_df['Elevation'] > -20000)]

            master_df = pd.concat([master_df, tile_df], ignore_index=True)

        except Exception as e:
            print(f"Error on tile {x},{y}: {e}")

        time.sleep(0.1) # Be polite to the Quickmap servers

# Save the final pristine dataset for the students
master_df.to_csv("lunar_pixels.csv", index=False)
print(f"Successfully generated lunar_pixels.csv with {len(master_df)} pixels!")
