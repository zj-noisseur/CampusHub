import json
from pathlib import Path

def file(club):
    # we use the Instagram handle as the filename for consistency sake
    filename = f"{club}.json"
    path = Path(__file__).resolve().parents[1] / 'export' / filename
    return path

# select a club within the admin portal
# obtain the IG handle and then pass it as the read file mechanism to the scraper
# if the json file does not yet exist, scraper will fetch the data


