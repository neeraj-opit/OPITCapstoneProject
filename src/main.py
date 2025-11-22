from utils.file_loader import load_files
from compare.column_comparison import compare_columns
from compare.datatype_comparison import compare_dtypes
from compare.id_comparison import compare_ids
from compare.row_comparison import compare_rows
from compare.generate_html import create_html_report

def main():
    PRIMARY_KEY = "ID"

    sf, laweb, dtype_map = load_files()

    # Defaults so report can still be generated
    missing_in_laweb = []
    missing_in_sf = []
    common_cols = []
    dtype_diff = []
    ids_in_sf_only = []
    ids_in_laweb_only = []
    row_diff = None

    if sf is not None and laweb is not None:
        missing_in_laweb, missing_in_sf, common_cols = compare_columns(sf, laweb)
        dtype_diff = compare_dtypes(sf, laweb, common_cols)
        ids_in_sf_only, ids_in_laweb_only = compare_ids(sf, laweb, PRIMARY_KEY)
        row_diff = compare_rows(sf, laweb, PRIMARY_KEY, common_cols, max_mismatches=500)

    create_html_report(
        sf,
        laweb,
        missing_in_laweb,
        missing_in_sf,
        dtype_diff,
        ids_in_sf_only,
        ids_in_laweb_only,
        row_diff,
        primary_key=PRIMARY_KEY,
    )

if __name__ == "__main__":
    main()
