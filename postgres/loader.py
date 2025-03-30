import pandas as pd
from .connection import get_engine
from .utils import sanitize_table_name
import logging

logger = logging.getLogger(__name__)

def load_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
    """
    Load a pandas DataFrame into the 'raw' schema of your Postgres warehouse.

    Args:
        df (pd.DataFrame): The DataFrame to load.
        table_name (str): Name of the table (no schema prefix!)
        if_exists (str): 'replace', 'append', or 'fail'
    """
    from .connection import get_engine
    from .utils import sanitize_table_name
    import logging

    logger = logging.getLogger(__name__)
    
    engine = get_engine()
    table_name = sanitize_table_name(table_name)

    with engine.begin() as conn:
        df.to_sql(table_name, con=conn, schema="raw", if_exists=if_exists, index=False)

    logger.info(f"Success! Loaded {len(df)} rows into 'raw.{table_name}' ({if_exists})")