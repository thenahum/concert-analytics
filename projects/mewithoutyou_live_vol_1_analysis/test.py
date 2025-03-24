import sys
import os

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_ROOT)

from setlistfm import setlist_dataframe
import pandas as pd
import logging


logging.basicConfig(level=logging.INFO)  # DEBUG < INFO < WARNING < ERROR < CRITICAL


# # Fetch and save 3 pages for testing
mbid = "759b5ff1-91fe-4ec9-b9b7-75b7b2ceb283"
setlist = setlist_dataframe("759b5ff1-91fe-4ec9-b9b7-75b7b2ceb283", name_hint="mewithoutYou")

pd.set_option("display.max_columns", None)  # Show all columns
pd.set_option("display.max_rows", 100)      # You can increase this if needed
pd.set_option("display.width", None)        # Don't wrap lines
pd.set_option("display.colheader_justify", "left")  # Align headers nicely

print(setlist.head())