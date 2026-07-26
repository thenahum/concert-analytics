from .connection import get_engine
from .utils import sanitize_table_name

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_table(table_name: str, engine=None, schema: str = "analytics_mart"):
    if engine is None:
        engine = get_engine()
    table_name = sanitize_table_name(table_name)
    if "." not in table_name:
        schema = sanitize_table_name(schema)
        table_name = f"{schema}.{table_name}"
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

def run_query(query: str, engine=None):
    if engine is None:
        engine = get_engine()
    return pd.read_sql(query, engine)
