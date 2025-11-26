from typing import List, Tuple
import pandas as pd


def compare_ids(sf: pd.DataFrame, laweb: pd.DataFrame, primary_key: str) -> Tuple[list, list]:
    """
    Compare IDs between SF & LAWEB.
    Returns:
      ids_in_sf_only, ids_in_laweb_only
    """
    pk = primary_key.strip().upper()

    sf_ids = set(sf[pk].dropna().unique())
    lw_ids = set(laweb[pk].dropna().unique())

    ids_in_sf_only = sorted(list(sf_ids - lw_ids))
    ids_in_laweb_only = sorted(list(lw_ids - sf_ids))

    return ids_in_sf_only, ids_in_laweb_only
