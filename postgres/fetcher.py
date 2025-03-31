from .connection import get_engine

from sqlalchemy import text, inspect
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_table(table_name: str, engine=None):
    if engine is None:
        engine = get_engine()
    return pd.read_sql(f"SELECT * FROM analytics_mart.{table_name}", engine)

def run_query(query: str, engine=None):
    if engine is None:
        engine = get_engine()
    return pd.read_sql(query, engine)