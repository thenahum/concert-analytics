import re
import logging

logger = logging.getLogger(__name__)

def sanitize_table_name(name: str) -> str:
    """
    Sanitizes a SQL table name with optional schema.
    Preserves schema.table structure, but cleans each part.
    """
    if "." in name:
        schema, table = name.split(".", 1)
        schema = re.sub(r"[^a-zA-Z0-9_]", "", schema)
        table = re.sub(r"[^a-zA-Z0-9_]", "", table)
        return f"{schema}.{table}"
    else:
        return re.sub(r"[^a-zA-Z0-9_]", "", name)