import pandas as pd


def load_csv_case_insensitive(path: str) -> pd.DataFrame:
    """
    Load a CSV file and normalize column names to UPPERCASE (case-insensitive matching).
    We let pandas infer dtypes so dtype comparison still works.
    """
    try:
        df = pd.read_csv(path)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin1")

    df.columns = [c.strip().upper() for c in df.columns]
    return df
