# setlistfm/client.py

# imports
from dotenv import load_dotenv
import os
import requests
import json
import time
import logging

logger = logging.getLogger(__name__)

# load enviornments with API Keys
load_dotenv()  # loads from .env by default
API_DELAY_SEC = 2

# Set API details
BASE_URL = "https://api.setlist.fm/rest/1.0"
HEADERS = {
    "x-api-key": os.getenv("SETLIST_FM_API_KEY"),
    "Accept": "application/json",
}

# Function to search for artist's MBID, takes string value, returns MBID 
def search_artist(name):
    url = f"{BASE_URL}/search/artists" #https://api.setlist.fm/docs/1.0/resource__1.0_search_artists.html
    params = {"artistName": name, "p": 1}
    response = requests.get(url, headers=HEADERS, params=params)

    logger.debug(f"Status code: {response.status_code} for URL: {response.url}")

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"API error: {e}")
        raise  # or handle/retry if you want

    return response.json() #https://api.setlist.fm/docs/1.0/json_Artists.html

# Function to get the first page of an artists setlist. Takes MBID, returns setlist JSON Object 
def get_artist_setlists(mbid):
    url = f"{BASE_URL}/artist/{mbid}/setlists" #https://api.setlist.fm/docs/1.0/resource__1.0_artist__mbid__setlists.html
    response = requests.get(url, headers=HEADERS)
    logger.debug(f"Status code: {response.status_code} for URL: {response.url}")

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"API error: {e}")
        raise  # or handle/retry if you want

    return response.json() #https://api.setlist.fm/docs/1.0/json_Setlists.html

# Function to get all pages for a specific artists unless you set a max page number
def get_all_setlists(mbid, max_pages=None):
    setlists = []
    page = 1

    while True:
        if page > 1:
            time.sleep(API_DELAY_SEC)  # apply delay *before* the next request

        url = f"{BASE_URL}/artist/{mbid}/setlists"
        response = requests.get(url, headers=HEADERS, params={"p": page})
        
        logger.debug(f"Status code: {response.status_code} for URL: {response.url}")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"API error: {e}")
            raise  # or handle/retry if you want
        
        data = response.json()

        setlists.extend(data.get("setlist", []))
        total = int(data.get("total", 0))
        items_per_page = int(data.get("itemsPerPage", 20))
        total_pages = (total + items_per_page - 1) // items_per_page

        logger.info(f"Fetched page {page}/{total_pages}")

        if max_pages and page >= max_pages:
            break
        if page >= total_pages:
            break

        page += 1

    return setlists