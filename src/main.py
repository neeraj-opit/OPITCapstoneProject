import argparse
import os
import pandas as pd

from utils.config_loader import load_table_config
from utils.file_loader import load_csv_case_insensitive
from compare.column_comparison import compare_columns
from compare.datatype_comparison import compare_dtypes
from compare.id_comparison import compare_ids
from compare.row_comparison import compare_rows
from rules.engine import evaluate_rules
from compare.generate_html import create_html_report


def build_rule_table_html(rule_results):
    if not rule_results:
        return "<p>No rules evaluated.</p>"

    rows = []
    for r in rule_results:
        status = r["result"]
        cls = (
            "rule-pass" if status == "PASS"
            else "rule-fail" if status == "FAIL"
            else "rule-skip"
        )
        rows.append(
            f"<tr>"
            f"<td>{r['id']}</td>"
            f"<td>{r['name']}</td>"
            f"<td>{r['priority']}</td>"
            f"<td class='{cls}'>{status}</td>"
            f"<td>{r.get('details','')}</td>"
            f"</tr>"
        )

    return (
        "<table>"
        "<tr><th>Rule ID</th><th>Name</th><th>Priority</th><th>Status</th><th>Details</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def run_comparison(sf_path, laweb_path, table_name, primary_key, dtype_map_path=None, enabled_rules=None):
    print(f"\n🚀 Running Comparison for: {table_name}")
    print("----------------------------------------")
    print(f"SF CSV Path:        {sf_path}")
    print(f"LAWEB CSV Path:     {laweb_path}")
    print(f"Primary Key (norm): {primary_key}")
    print(f"DType Mapping File: {dtype_map_path if dtype_map_path else '(none → using inferred dtypes)'}")

    # Load CSVs
    sf = load_csv_case_insensitive(sf_path)
    laweb = load_csv_case_insensitive(laweb_path)

    pk = primary_key.strip().upper()
    if pk not in sf.columns:
        raise ValueError(f"Primary key '{pk}' not found in SF columns.")
    if pk not in laweb.columns:
        raise ValueError(f"Primary key '{pk}' not found in LAWEB columns.")

    # Column comparison
    common_cols, missing_in_sf, missing_in_laweb = compare_columns(sf, laweb)

    missing_html_parts = []
    if missing_in_sf:
        missing_html_parts.append(
            "<h4>Columns present in LAWEB but missing in SF</h4><pre>"
            + "\n".join(missing_in_sf)
            + "</pre>"
        )
    else:
        missing_html_parts.append("<p>No columns missing in SF.</p>")

    if missing_in_laweb:
        missing_html_parts.append(
            "<h4>Columns present in SF but missing in LAWEB</h4><pre>"
            + "\n".join(missing_in_laweb)
            + "</pre>"
        )
    else:
        missing_html_parts.append("<p>No columns missing in LAWEB.</p>")

    column_mismatch_html = "".join(missing_html_parts)

    # Dtype comparison (inferred)
    dtype_map_df = None
    if dtype_map_path and os.path.exists(dtype_map_path):
        try:
            dtype_map_df = pd.read_excel(dtype_map_path)
        except Exception:
            dtype_map_df = None  # ignore if invalid

    dtype_diff_df = compare_dtypes(sf, laweb, common_cols, dtype_map_df)
    if dtype_diff_df is not None and not dtype_diff_df.empty:
        dtype_diff_html = dtype_diff_df.to_html(index=False)
    else:
        dtype_diff_html = "<p>No datatype differences detected.</p>"

    # ID comparison
    ids_sf_only, ids_laweb_only = compare_ids(sf, laweb, pk)
    id_parts = [
        f"<h4>IDs present in SF but missing in LAWEB ({len(ids_sf_only)})</h4>"
        + "<pre>" + "\n".join(map(str, ids_sf_only[:200])) + "</pre>",
        f"<h4>IDs present in LAWEB but missing in SF ({len(ids_laweb_only)})</h4>"
        + "<pre>" + "\n".join(map(str, ids_laweb_only[:200])) + "</pre>",
    ]
    id_diff_html = "".join(id_parts)

    # Row-level comparison (sample for HTML + CM01)
    row_diff_df = compare_rows(sf, laweb, pk, common_cols, max_mismatches=100)
    if row_diff_df is not None and not row_diff_df.empty:
        styled = row_diff_df.copy()
        styled["value_sf"] = styled["value_sf"].apply(lambda v: f"<span class='sf-cell'>{v}</span>")
        styled["value_laweb"] = styled["value_laweb"].apply(lambda v: f"<span class='lw-cell'>{v}</span>")
        row_diff_html = styled.to_html(escape=False, index=False)
    else:
        row_diff_html = "<p>No row-level mismatches found (sample up to 100 rows).</p>"

    # Data Quality Rule Engine (now includes CM02 + CM03)
    dq_summary = evaluate_rules(
        sf=sf,
        laweb=laweb,
        common_cols=common_cols,
        pk=pk,
        column_missing_sf=missing_in_sf,
        column_missing_laweb=missing_in_laweb,
        ids_sf_only=ids_sf_only,
        ids_laweb_only=ids_laweb_only,
        row_diff=row_diff_df,
        enabled_rules=enabled_rules,
    )

    # Console scorecard
    print("\n📊 Data Quality Scorecard")
    print("------------------------")
    print(
        f"Overall Score: {dq_summary['score']}%\n"
        f"Passed: {dq_summary['passed']} | "
        f"Failed: {dq_summary['failed']} | "
        f"Skipped: {dq_summary['skipped']} | "
        f"Critical Failed: {dq_summary['critical_failed']}"
    )
    for r in dq_summary["rules"]:
        print(f"- {r['id']} [{r['priority']}] -> {r['result']}: {r['name']}")

    # Rule breakdown HTML
    rule_table_html = build_rule_table_html(dq_summary["rules"])

    # Generate HTML dashboard
    create_html_report(
        table_name=table_name,
        score=dq_summary["score"],
        passed=dq_summary["passed"],
        failed=dq_summary["failed"],
        skipped=dq_summary["skipped"],
        critical_failed=dq_summary["critical_failed"],
        rule_table_html=rule_table_html,
        missing_columns_html=column_mismatch_html,
        dtype_diff_html=dtype_diff_html,
        id_diff_html=id_diff_html,
        row_diff_html=row_diff_html,
    )


def main():
    parser = argparse.ArgumentParser(description="SF vs LAWEB Data Comparison Framework")
    parser.add_argument("--table", help="Table name from YAML mapping", required=False)
    parser.add_argument("--sf", help="Path to SF CSV file", required=False)
    parser.add_argument("--laweb", help="Path to LAWEB CSV file", required=False)
    parser.add_argument("--pk", help="Primary key column name (for direct mode)", required=False)

    args = parser.parse_args()

    # Mode 1: YAML table-based
    if args.table:
        tables_cfg = load_table_config()
        if args.table not in tables_cfg:
            raise ValueError(f"Table '{args.table}' not found in table_mapping.yaml")

        entry = tables_cfg[args.table]
        enabled_rules = entry.get("rules_enabled")

        run_comparison(
            sf_path=entry["sf"],
            laweb_path=entry["laweb"],
            table_name=args.table,
            primary_key=entry["primary_key"],
            dtype_map_path=entry.get("dtype_map"),
            enabled_rules=enabled_rules,
        )
        return

    # Mode 2: Direct CSV mode
    if args.sf and args.laweb and args.pk:
        run_comparison(
            sf_path=args.sf,
            laweb_path=args.laweb,
            table_name="DirectComparison",
            primary_key=args.pk,
            dtype_map_path=None,
            enabled_rules=None,
        )
        return

    print("\n❗ Not enough arguments.")
    print("Use either:")
    print("  python3 src/main.py --table Guarantee")
    print("or direct mode:")
    print("  python3 src/main.py --sf path/to/sf.csv --laweb path/to/laweb.csv --pk ID")


if __name__ == "__main__":
    main()
