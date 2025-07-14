import os
import time
import requests
import pandas as pd
import ast

# Load CSV
df = pd.read_csv('property_images.csv')
print(df.head())

# Safely evaluate the image_urls column
df["image_urls"] = df["image_urls"].fillna("").apply(lambda x: x.split(",") if x else [])

# Image downloader function
def download_image(url, folder, filename=None):
    try:
        os.makedirs(folder, exist_ok=True)

        if not filename:
            filename = url.split("/")[-1].split("?")[0]  # cleaner file name

        filepath = os.path.join(folder, filename)

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        time.sleep(3)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"✅ Saved: {filepath}")

    except Exception as e:
        print(f"❌ Failed to download {url}\nError: {e}")

# Main download loop
for i, property_id in enumerate(df["property_id"]):
    folder_address = f"test_images/{property_id}"

    for image_url in df.loc[i, "image_urls"]:
        download_image(image_url, folder=folder_address)
