import time
from io import BytesIO

import numpy as np
import pandas as pd
import requests
from PIL import Image

# Target region: Eastern edge of Mare Serenitatis (stark contrast area)
zoom = 9
x_range = range(298, 303)
y_range = range(88, 93)

url_albedo = "https://lroc-tiles.quickmap.io/tiles/lola_albedo/lunar-fulleqc/{zoom}/{x}/{y}.flt?size=256"
url_dtm = "https://lroc-tiles.quickmap.io/tiles/qts_demstack/lunar-fulleqc/{zoom}/{x}/{y}.flt?size=256"
url_mask = (
    "https://lroc-tiles.quickmap.io/tiles/lmare_bfill/lunar-fulleqc/{zoom}/{x}/{y}.png"
)

master_df = pd.DataFrame()

# The magic numbers we discovered
expected_flt_bytes = 262153
header_offset = 9

print("Starting Lunar Pixel Extraction...")

for x in x_range:
    for y in y_range:
        try:
            # 1. Fetch & Decode Albedo (stripping the 9-byte header)
            r_albedo = requests.get(url_albedo.format(zoom=zoom, x=x, y=y), timeout=10)
            if (
                r_albedo.status_code != 200
                or len(r_albedo.content) != expected_flt_bytes
            ):
                continue
            albedo_arr = np.frombuffer(
                r_albedo.content[header_offset:], dtype=np.float32
            )

            # 2. Fetch & Decode Elevation (stripping the 9-byte header)
            r_dtm = requests.get(url_dtm.format(zoom=zoom, x=x, y=y), timeout=10)
            if r_dtm.status_code != 200 or len(r_dtm.content) != expected_flt_bytes:
                continue
            dtm_arr = np.frombuffer(r_dtm.content[header_offset:], dtype=np.float32)

            # 3. Fetch the Ground Truth Mask (PNG)
            r_mask = requests.get(url_mask.format(zoom=zoom, x=x, y=y), timeout=10)
            if r_mask.status_code == 200 and len(r_mask.content) > 0:
                try:
                    img = Image.open(BytesIO(r_mask.content)).convert("RGBA")
                    # FORCE the mask to match our 256x256 data grids!
                    # We use NEAREST to preserve the hard boundaries without blurring them
                    img = img.resize((256, 256), Image.NEAREST)

                    alpha_channel = np.array(img)[:, :, 3].flatten()
                    labels = np.where(alpha_channel > 0, 1, 2)  # 1: Mare, 2: Highland
                except Exception as mask_err:
                    print(f"  -> Mask image error: {mask_err}. Defaulting to Highland.")
                    labels = np.full(256 * 256, 2)
            else:
                # If there's no mare boundary drawn here, it's pure highlands
                labels = np.full(256 * 256, 2)

            # 4. Assemble the Tile
            tile_df = pd.DataFrame(
                {"Albedo": albedo_arr, "Elevation": dtm_arr, "Class": labels}
            )

            # Filter out extreme "No Data" voids from the spacecraft sensors
            tile_df = tile_df[
                (tile_df["Albedo"] > -100) & (tile_df["Elevation"] > -20000)
            ]

            master_df = pd.concat([master_df, tile_df], ignore_index=True)
            print(f"Processed {zoom}/{x}/{y} -> Added {len(tile_df)} pixels.")

        except Exception as e:
            print(f"Error on tile {x},{y}: {e}")

        time.sleep(0.1)  # Be polite to their servers

# Save the final pristine dataset
master_df.to_csv("lunar_pixels.csv", index=False)
print(f"\nSUCCESS! Saved lunar_pixels.csv with {len(master_df)} valid measurements.")
