"""Check that the YouTube Data API key in .env works."""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()                                   # reads .env into environment variables
key = os.environ.get("YOUTUBE_API_KEY")
if not key:
    sys.exit("YOUTUBE_API_KEY is not set in .env")

resp = requests.get(
    "https://www.googleapis.com/youtube/v3/search",
    params={
        "part": "snippet",          # return titles and descriptions
        "q": "SNIK official video", # the search query
        "type": "video",
        "maxResults": 3,
        "key": key,
    },
    timeout=30,
)

if resp.status_code != 200:
    sys.exit(f"Error {resp.status_code}: {resp.text[:500]}")

for item in resp.json()["items"]:
    print(item["snippet"]["title"], "|", item["id"]["videoId"])
