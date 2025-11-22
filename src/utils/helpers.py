def safe_len(obj) -> int:
    """Return len(obj) but handle None as 0."""
    if obj is None:
        return 0
    try:
        return len(obj)
    except TypeError:
        return 0
