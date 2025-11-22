import os
import pandas as pd

def try_load_csv(path: str):
    """Load a CSV file if it exists, else return None."""
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def try_load_excel(path: str):
    """Load an Excel file if it exists, else return None."""
    if os.path.exists(path):
        return pd.read_excel(path)
    return None

def load_files():
    """Load SF, LAWEB and dtype mapping files, normalizing column names if present."""
    sf_path = "data/raw/guarantee_sf.csv"
    laweb_path = "data/raw/guarantee_laweb.csv"
    dtype_path = "data/raw/DTypes_GuaranteeTable_Sf_VS_Laweb.xlsx"

    sf = try_load_csv(sf_path)
    laweb = try_load_csv(laweb_path)
    dtype_map = try_load_excel(dtype_path)

    # Normalize column names to UPPERCASE + strip spaces
    if sf is not None:
        sf.columns = sf.columns.str.upper().str.strip()
    if laweb is not None:
        laweb.columns = laweb.columns.str.upper().str.strip()

    return sf, laweb, dtype_map
