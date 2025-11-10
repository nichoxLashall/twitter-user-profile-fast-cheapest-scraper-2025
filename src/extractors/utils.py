# Utility functions (e.g., for API requests, parsing)
def normalize_username(username: str) -> str:
    """
    Normalize the username (e.g., handle @username case).
    """
    return username.lstrip('@')