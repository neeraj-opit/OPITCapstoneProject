import os


def create_html_report(
    table_name: str,
    score: float,
    passed: int,
    failed: int,
    skipped: int,
    critical_failed: int,
    rule_table_html: str,
    missing_columns_html: str,
    dtype_diff_html: str,
    id_diff_html: str,
    row_diff_html: str,
    output_folder: str = "reports/html",
) -> str:
    """
    Generate a HTML dashboard-style report.
    """

    # Gauge segments: red (0-50), orange (50-70), green (70-100)
    score = float(score)
    score_fail_deg = max(0.0, min(score, 50.0)) * 3.6
    score_warn_deg = max(0.0, min(score - 50.0, 20.0)) * 3.6
    score_pass_deg = max(0.0, max(score - 70.0, 0.0)) * 3.6

    template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<title>{{table_name}} – Data Quality Dashboard</title>

<style>
    body {
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
        background: #121417;
        color: #e8e8e8;
        margin: 0;
        padding: 0;
    }
    .header {
        background: linear-gradient(135deg,#007bff,#003d99);
        padding: 30px;
        text-align:center;
        font-size:30px;
        font-weight:bold;
        color:white;
        box-shadow:0 3px 10px rgba(0,0,0,0.4);
    }
    .container { width:94%; margin:20px auto; }
    .card {
        background: rgba(255,255,255,0.07);
        border-radius:14px;
        padding:20px;
        margin-bottom:25px;
        box-shadow:0 4px 14px rgba(0,0,0,0.35);
    }
    .flex-row { display:flex; flex-wrap:wrap; gap:20px; }
    .gauge {
        width:260px;height:260px;border-radius:50%;
        background: conic-gradient(
            #ff3d3d {{score_fail_deg}}deg,
            #ffcc00 {{score_warn_deg}}deg,
            #00cc66 {{score_pass_deg}}deg
        );
        display:flex;align-items:center;justify-content:center;
    }
    .gauge-center {
        width:180px;height:180px;border-radius:50%;
        background:#121417;
        font-size:42px;font-weight:bold;color:#00ff9d;
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 0 18px rgba(0,255,157,0.45);
    }
    .summary-box { flex:1;min-width:200px;text-align:center; }
    .summary-value { font-size:34px;font-weight:bold; }
    .pass{color:#00ff9d;} .fail{color:#ff5252;} .warn{color:#ffcc00;}

    details {
        background: rgba(255,255,255,0.06);
        padding:14px;border-radius:12px;margin-bottom:20px;
        box-shadow:0 2px 6px rgba(0,0,0,0.4);
    }
    summary {font-size:20px;font-weight:bold;cursor:pointer;}

    table{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px;}
    th{background:#1f2937;padding:10px;}
    td{padding:7px;border-bottom:1px solid #333;}
    tr:nth-child(even){background:#1a1f25;}
    tr:hover{background:#28333f;}

    .rule-pass{color:#00ff9d;font-weight:bold;}
    .rule-fail{color:#ff6666;font-weight:bold;}
    .rule-skip{color:#ffcc00;font-weight:bold;}

    .sf-cell{background:#661111;color:#ffbaba;padding:3px;border-radius:4px;}
    .lw-cell{background:#0d4d22;color:#9effc2;padding:3px;border-radius:4px;}

</style>
</head>

<body>
<div class="header">{{table_name}} – Data Quality Dashboard </div>

<div class="container">

<div class="flex-row">

    <div class="card" style="flex:0 0 280px">
        <h2 style="text-align:center;margin-bottom:10px;">Overall Quality</h2>
        <div class="gauge"><div class="gauge-center">{{score}}%</div></div>
    </div>

    <div class="card" style="flex:1;">
        <h2>Summary Statistics</h2>
        <div class="flex-row">
            <div class="summary-box"><h3>Passed</h3>
                <div class="summary-value pass">{{passed}}</div></div>
            <div class="summary-box"><h3>Failed</h3>
                <div class="summary-value fail">{{failed}}</div></div>
            <div class="summary-box"><h3>Skipped</h3>
                <div class="summary-value warn">{{skipped}}</div></div>
            <div class="summary-box"><h3>Critical Failures</h3>
                <div class="summary-value fail">{{critical_failed}}</div></div>
        </div>
    </div>
</div>

<details open><summary>Rule Breakdown</summary>
{{rule_table}}
</details>

<details><summary>Missing / Extra Columns</summary>
{{missing_columns}}
</details>

<details><summary>Datatype Differences</summary>
{{dtype_diff}}
</details>

<details><summary>ID Mismatch Summary</summary>
{{id_diff}}
</details>

<details><summary>Row-level Mismatches (first 100)</summary>
{{row_diff}}
</details>

</div>
</body>
</html>
"""

    html = (
        template.replace("{{table_name}}", str(table_name))
        .replace("{{score}}", str(score))
        .replace("{{passed}}", str(passed))
        .replace("{{failed}}", str(failed))
        .replace("{{skipped}}", str(skipped))
        .replace("{{critical_failed}}", str(critical_failed))
        .replace("{{score_fail_deg}}", str(score_fail_deg))
        .replace("{{score_warn_deg}}", str(score_warn_deg))
        .replace("{{score_pass_deg}}", str(score_pass_deg))
        .replace("{{rule_table}}", rule_table_html)
        .replace("{{missing_columns}}", missing_columns_html)
        .replace("{{dtype_diff}}", dtype_diff_html)
        .replace("{{id_diff}}", id_diff_html)
        .replace("{{row_diff}}", row_diff_html)
    )

    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.join(output_folder, f"{table_name}_comparison_report.html")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ HTML report generated: {filename}")
    return filename


# Backward-compat alias if older code imports this name
generate_html_report = create_html_report
