from typing import List
import pandas as pd


def compare_rows(
    sf: pd.DataFrame,
    laweb: pd.DataFrame,
    primary_key: str,
    common_cols: List[str],
    max_mismatches: int = 100,
) -> pd.DataFrame:
    """
    Row-level comparison between SF & LAWEB.

    - Joins on primary_key (inner join).
    - For each common column, checks where values differ.
    - Returns a "long" DataFrame with columns:
        PK, COLUMN, value_sf, value_laweb
    - Limits to max_mismatches to keep HTML report readable.
    """
    pk = primary_key.strip().upper()

    merged = sf.merge(laweb, on=pk, how="inner", suffixes=("_SF", "_LAWEB"))

    results = []
    count = 0

    for col in common_cols:
        col_sf = f"{col}_SF"
        col_lw = f"{col}_LAWEB"

        if col_sf not in merged.columns or col_lw not in merged.columns:
            continue

        sf_series = merged[col_sf].fillna("__NA__")
        lw_series = merged[col_lw].fillna("__NA__")

        diff_mask = sf_series != lw_series
        diff_indices = merged.index[diff_mask]

        for idx in diff_indices:
            if count >= max_mismatches:
                break

            pk_val = merged.at[idx, pk]
            val_sf = sf_series.at[idx]
            val_lw = lw_series.at[idx]

            results.append(
                {
                    "PK": pk_val,
                    "COLUMN": col,
                    "value_sf": str(val_sf),
                    "value_laweb": str(val_lw),
                }
            )
            count += 1

        if count >= max_mismatches:
            break

    if not results:
        return pd.DataFrame(columns=["PK", "COLUMN", "value_sf", "value_laweb"])

    return pd.DataFrame(results)
