from typing import List, Tuple
import pandas as pd


def compare_columns(sf: pd.DataFrame, laweb: pd.DataFrame) -> Tuple[list, list, list]:
    """
    Compare column sets between SF and LAWEB.
    Both DataFrames are expected to already have UPPERCASE column names.
    Returns:
      common_cols, missing_in_sf, missing_in_laweb
    """
    sf_cols = set(sf.columns)
    lw_cols = set(laweb.columns)

    common_cols = sorted(sf_cols & lw_cols)
    missing_in_sf = sorted(lw_cols - sf_cols)       # present in LAWEB, missing in SF
    missing_in_laweb = sorted(sf_cols - lw_cols)    # present in SF, missing in LAWEB

    return common_cols, missing_in_sf, missing_in_laweb
