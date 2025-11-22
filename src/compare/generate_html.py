import pandas as pd
from utils.helpers import safe_len

def create_html_report(
    sf,
    laweb,
    missing_in_laweb,
    missing_in_sf,
    dtype_diff,
    ids_sf_only,
    ids_laweb_only,
    row_diff,
    primary_key="ID",
    output="reports/html/guarantee_comparison_report.html",
):
    total_sf_cols = len(sf.columns) if sf is not None else 0
    total_laweb_cols = len(laweb.columns) if laweb is not None else 0
    total_sf_rows = len(sf) if sf is not None else 0
    total_laweb_rows = len(laweb) if laweb is not None else 0

    if sf is not None and laweb is not None and primary_key in sf.columns and primary_key in laweb.columns:
        common_ids = len(sf.merge(laweb, on=primary_key, how="inner"))
    else:
        common_ids = 0

    dtype_df = pd.DataFrame(dtype_diff) if dtype_diff else pd.DataFrame(columns=["column", "sf_dtype", "laweb_dtype"])

    warning_messages = []
    if sf is None:
        warning_messages.append("SF file not found – SF-related analysis is limited or unavailable.")
    if laweb is None:
        warning_messages.append("LAWEB file not found – LAWEB-related analysis is limited or unavailable.")

    html = []
    html.append("<html><head><meta charset='UTF-8'><title>Guarantee Comparison Report</title>")
    html.append("""
    <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f7fb; }
    h1, h2 { color: #1f3b57; }
    .warning { background: #fff3cd; border: 1px solid #ffeeba; padding: 10px; margin-bottom: 10px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; background: #fff; }
    th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }
    th { background: #1f3b57; color: #fff; }
    .sf-cell { background: #e2f0ff; }
    .laweb-cell { background: #ffe2e2; }
    </style>
    """)
    html.append("</head><body>")
    html.append("<h1>Guarantee Table Comparison Report</h1>")

    for w in warning_messages:
        html.append(f"<div class='warning'>{w}</div>")

    html.append("<h2>Summary</h2>")
    html.append("<table>")
    html.append("<tr><th>Metric</th><th>Value</th></tr>")
    html.append(f"<tr><td>Columns (SF)</td><td>{total_sf_cols}</td></tr>")
    html.append(f"<tr><td>Columns (LAWEB)</td><td>{total_laweb_cols}</td></tr>")
    html.append(f"<tr><td>Rows (SF)</td><td>{total_sf_rows}</td></tr>")
    html.append(f"<tr><td>Rows (LAWEB)</td><td>{total_laweb_rows}</td></tr>")
    html.append(f"<tr><td>Rows with common {primary_key}</td><td>{common_ids}</td></tr>")
    html.append(f"<tr><td>Columns missing in LAWEB</td><td>{len(missing_in_laweb)}</td></tr>")
    html.append(f"<tr><td>Columns missing in SF</td><td>{len(missing_in_sf)}</td></tr>")
    html.append(f"<tr><td>Datatype mismatches</td><td>{len(dtype_df)}</td></tr>")
    html.append(f"<tr><td>{primary_key}s only in SF</td><td>{safe_len(ids_sf_only)}</td></tr>")
    html.append(f"<tr><td>{primary_key}s only in LAWEB</td><td>{safe_len(ids_laweb_only)}</td></tr>")
    html.append(f"<tr><td>Row mismatches (sample)</td><td>{safe_len(row_diff)}</td></tr>")
    html.append("</table>")

    # Column comparison
    html.append("<h2>Columns present in SF but missing in LAWEB</h2>")
    if missing_in_laweb:
        html.append("<ul>")
        for c in missing_in_laweb:
            html.append(f"<li>{c}</li>")
        html.append("</ul>")
    else:
        html.append("<p><em>None</em></p>")

    html.append("<h2>Columns present in LAWEB but missing in SF</h2>")
    if missing_in_sf:
        html.append("<ul>")
        for c in missing_in_sf:
            html.append(f"<li>{c}</li>")
        html.append("</ul>")
    else:
        html.append("<p><em>None</em></p>")

    # Datatype mismatches
    html.append("<h2>Datatype mismatches</h2>")
    if not dtype_df.empty:
        html.append(dtype_df.to_html(index=False))
    else:
        html.append("<p><em>No datatype mismatches.</em></p>")

    # Row-level mismatches
    html.append(f"<h2>Row-level mismatches by {primary_key}</h2>")
    if row_diff is not None and not row_diff.empty:
        styled = row_diff.copy()
        styled["value_sf"] = styled["value_sf"].apply(lambda v: f"<span class='sf-cell'>{v}</span>")
        styled["value_laweb"] = styled["value_laweb"].apply(lambda v: f"<span class='laweb-cell'>{v}</span>")
        html.append(styled.to_html(index=False, escape=False))
    else:
        html.append("<p><em>No row-level mismatches in sample.</em></p>")

    html.append("</body></html>")

    html_str = "\n".join(html)
    with open(output, "w", encoding="utf-8") as f:
        f.write(html_str)

    print(f"HTML report generated: {output}")
