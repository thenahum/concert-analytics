import re
import logging

logger = logging.getLogger(__name__)

def sanitize_table_name(name: str) -> str:
    """
    Sanitizes a string to be a valid SQL table name:
    - lowercases
    - replaces spaces with underscores
    - removes invalid characters
    """
    name = name.lower().replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    return name