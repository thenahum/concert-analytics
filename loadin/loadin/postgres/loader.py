from .connection import get_engine
from .utils import sanitize_table_name

from sqlalchemy import text, inspect
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_dataframe(table_name: str, df: pd.DataFrame, if_exists: str = "replace"):
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

def refresh_raw_table(table_name: str, df: pd.DataFrame):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM raw.{table_name}"))
        df.to_sql(table_name, con=conn, schema="raw", if_exists="append", index=False)
    print(f"Success! Refreshed raw.{table_name} with {len(df)} rows")


def upsert_raw_table(table_name: str, df: pd.DataFrame):
    """
    Upserts data into raw schema. If table exists, DELETE only rows with matching `name_hint` values.
    If not, creates it. Handles errors gracefully.
    """
    engine = get_engine()

    if "name_hint" not in df.columns:
        logger.error("FAIL! `name_hint` column is required for upsert logic.")
        return

    try:
        with engine.begin() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names(schema="raw")

            if table_name in tables:
                logger.info(f"🔁 Table raw.{table_name} exists — deleting matching rows.")
                
                # Get unique name_hint values and build a bind parameter list
                name_hints = df["name_hint"].dropna().unique().tolist()
                if not name_hints:
                    logger.warning("No name_hint values to match on; skipping delete step.")
                else:
                    placeholders = ", ".join([f":val{i}" for i in range(len(name_hints))])
                    delete_query = text(f"DELETE FROM raw.{table_name} WHERE name_hint IN ({placeholders})")
                    conn.execute(delete_query, {f"val{i}": v for i, v in enumerate(name_hints)})

                df.to_sql(table_name, con=conn, schema="raw", if_exists="append", index=False)
            else:
                logger.info(f"🆕 Table raw.{table_name} does not exist — creating and loading.")
                df.to_sql(table_name, con=conn, schema="raw", if_exists="replace", index=False)

        logger.info(f"SUCCESS! Upserted raw.{table_name} with {len(df)} rows.")

    except Exception as e:
        logger.error(f"FAIL! Failed to upsert raw.{table_name}: {e}")