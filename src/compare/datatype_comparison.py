from typing import List, Optional
import pandas as pd


def compare_dtypes(
    sf: pd.DataFrame,
    laweb: pd.DataFrame,
    common_cols: List[str],
    dtype_map_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Compare pandas-inferred dtypes between SF & LAWEB for the common columns.

    NOTE:
    - For now we ignore dtype_map_df (Excel) to avoid format issues.
    - We simply show where SF and LAWEB dtypes differ.

    Returns a DataFrame with:
      COLUMN, SF_DTYPE, LAWEB_DTYPE, MATCH, REASON
    """
    rows = []
    for col in common_cols:
        sf_dtype = str(sf[col].dtype)
        lw_dtype = str(laweb[col].dtype)

        if sf_dtype == lw_dtype:
            continue

        rows.append(
            {
                "COLUMN": col,
                "SF_DTYPE": sf_dtype,
                "LAWEB_DTYPE": lw_dtype,
                "MATCH": False,
                "REASON": "Inferred dtype mismatch",
            }
        )

    if not rows:
        return pd.DataFrame(columns=["COLUMN", "SF_DTYPE", "LAWEB_DTYPE", "MATCH", "REASON"])

    return pd.DataFrame(rows)
