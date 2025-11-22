from typing import List
import pandas as pd

def compare_rows(sf, laweb, pk: str, common_cols: list, max_mismatches: int = 500) -> pd.DataFrame:
    """
    Row-level value comparison between SF and LAWEB on common IDs and columns.

    Returns a DataFrame with columns:
        pk, column, value_sf, value_laweb
    """
    if sf is None or laweb is None:
        return pd.DataFrame(columns=[pk, "column", "value_sf", "value_laweb"])

    if pk not in sf.columns or pk not in laweb.columns:
        return pd.DataFrame(columns=[pk, "column", "value_sf", "value_laweb"])

    merged = sf.merge(laweb, on=pk, how="inner", suffixes=("_SF", "_LAWEB"))

    mismatches_records = []

    for col in common_cols:
        if col == pk:
            continue

        col_sf = f"{col}_SF"
        col_laweb = f"{col}_LAWEB"

        if col_sf not in merged.columns or col_laweb not in merged.columns:
            continue

        # Convert to object, fill NaNs with same placeholder, then compare
        sf_col = merged[col_sf].astype("object").fillna("__NA__").infer_objects(copy=False)
        laweb_col = merged[col_laweb].astype("object").fillna("__NA__").infer_objects(copy=False)

        diff_mask = sf_col != laweb_col
        diff_rows = merged[diff_mask][[pk, col_sf, col_laweb]]

        for _, row in diff_rows.iterrows():
            mismatches_records.append(
                {
                    pk: row[pk],
                    "column": col,
                    "value_sf": row[col_sf],
                    "value_laweb": row[col_laweb],
                }
            )
            if len(mismatches_records) >= max_mismatches:
                break

        if len(mismatches_records) >= max_mismatches:
            break

    if mismatches_records:
        return pd.DataFrame(mismatches_records)
    else:
        return pd.DataFrame(columns=[pk, "column", "value_sf", "value_laweb"])
