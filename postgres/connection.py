import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def get_engine():
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT")
    db = os.getenv("PGDATABASE")

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(db_url)