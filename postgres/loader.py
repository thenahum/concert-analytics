import pandas as pd
from .connection import get_engine
from .utils import sanitize_table_name
import logging

logger = logging.getLogger(__name__)

def load_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
    """
    Load a pandas DataFrame into Postgres.

    Args:
        df (pd.DataFrame): The DataFrame to load.
        table_name (str): Name of the destination table.
        if_exists (str): 'replace', 'append', or 'fail'.
        verbose (bool): Whether to print a status message.
    """
    engine = get_engine()
    table_name = sanitize_table_name(table_name)

    with engine.begin() as conn:
        df.to_sql(table_name, con=conn, if_exists=if_exists, index=False)
    
    logger.info(f"Loaded {len(df)} rows into '{table_name}' ({if_exists})")