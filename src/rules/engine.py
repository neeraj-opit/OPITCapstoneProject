from typing import Dict, Any, List, Optional, Sequence
import yaml
import os
import pandas as pd


def _weight_for_priority(priority: str) -> float:
    """
    Map rule priority to numeric weight.
    """
    p = (priority or "").strip().lower()
    if p == "critical":
        return 3.0
    if p == "high":
        return 2.0
    if p == "medium":
        return 1.0
    if p == "low":
        return 0.5
    return 1.0


def load_rules_config(path: str = "config/data_quality_rules.yaml") -> Dict[str, Any]:
    """
    Load the data quality rules YAML.

    Expected structure:

    rules:
      V01:
        name: "Record Count Match"
        type: "row_count"
        priority: "Critical"
        enabled: true
        tolerance: 0
      ...
      CM02:
        name: "Full Row Match"
        type: "full_row_compare"
        priority: "High"
        enabled: true
      CM03:
        name: "Null Pattern Consistency"
        type: "null_pattern"
        priority: "Medium"
        enabled: true
        threshold: 20.0
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Rules configuration not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data.get("rules", {})


def _compute_full_row_mismatch_count(
    sf: pd.DataFrame,
    laweb: pd.DataFrame,
    pk: str,
    common_cols: List[str],
) -> int:
    """
    Compute how many joined rows (by PK) have at least one differing value
    across any of the common columns.
    """
    pk = pk.strip().upper()
    merged = sf.merge(laweb, on=pk, how="inner", suffixes=("_SF", "_LAWEB"))
    if merged.empty:
        return 0

    mismatch_mask = pd.Series(False, index=merged.index)

    for col in common_cols:
        col_sf = f"{col}_SF"
        col_lw = f"{col}_LAWEB"
        if col_sf not in merged.columns or col_lw not in merged.columns:
            continue
        a = merged[col_sf].fillna("__NA__")
        b = merged[col_lw].fillna("__NA__")
        mismatch_mask = mismatch_mask | (a != b)

    return int(mismatch_mask.sum())


def _compute_null_pattern_violations(
    sf: pd.DataFrame,
    laweb: pd.DataFrame,
    common_cols: List[str],
    threshold_pct: float = 20.0,
) -> List[Dict[str, Any]]:
    """
    For each common column, compare NULL percentage between SF and LAWEB.
    Returns a list of columns where the difference exceeds threshold_pct.
    """
    violations: List[Dict[str, Any]] = []

    for col in common_cols:
        sf_null_pct = float(sf[col].isna().mean() * 100.0)
        lw_null_pct = float(laweb[col].isna().mean() * 100.0)
        diff_pct = abs(sf_null_pct - lw_null_pct)

        if diff_pct > threshold_pct:
            violations.append(
                {
                    "column": col,
                    "sf_null_pct": round(sf_null_pct, 2),
                    "laweb_null_pct": round(lw_null_pct, 2),
                    "diff_pct": round(diff_pct, 2),
                }
            )

    # Sort by severity (biggest diff first)
    violations.sort(key=lambda x: x["diff_pct"], reverse=True)
    return violations


def evaluate_rules(
    sf: pd.DataFrame,
    laweb: pd.DataFrame,
    common_cols: List[str],
    pk: str,
    column_missing_sf: List[str],
    column_missing_laweb: List[str],
    ids_sf_only: List[Any],
    ids_laweb_only: List[Any],
    row_diff: pd.DataFrame,
    enabled_rules: Optional[Sequence[str]] = None,
    rules_path: str = "config/data_quality_rules.yaml",
) -> Dict[str, Any]:
    """
    Evaluate configured rules and return summary & per-rule results.

    Returns dict:
      {
        "score": float,
        "passed": int,
        "failed": int,
        "skipped": int,
        "critical_failed": int,
        "rules": [ {id, name, priority, result, details}, ... ]
      }
    """
    pk = pk.strip().upper()

    rules_cfg = load_rules_config(rules_path)

    sf_rows = len(sf)
    lw_rows = len(laweb)
    sf_cols = len(sf.columns)
    lw_cols = len(laweb.columns)

    results: List[Dict[str, Any]] = []
    passed = failed = skipped = critical_failed = 0
    total_weight = 0.0
    gained_weight = 0.0

    full_mismatch_count: Optional[int] = None  # for CM02
    null_pattern_cache: Optional[List[Dict[str, Any]]] = None  # for CM03

    for rule_id, rule_def in rules_cfg.items():
        # Per-table rule filtering (from table_mapping.yaml)
        if enabled_rules is not None and rule_id not in enabled_rules:
            continue  # completely ignore, not even SKIPPED

        enabled = rule_def.get("enabled", True)
        name = rule_def.get("name", "")
        priority = rule_def.get("priority", "Medium")
        r_type = rule_def.get("type", "").strip()
        tolerance = rule_def.get("tolerance", 0)

        if not enabled:
            results.append(
                {
                    "id": rule_id,
                    "name": name,
                    "priority": priority,
                    "result": "SKIPPED",
                    "details": "Rule disabled in config.",
                }
            )
            skipped += 1
            continue

        weight = _weight_for_priority(priority)
        result = "SKIPPED"
        details = ""

        # -------------- RULE LOGIC --------------

        if r_type == "row_count":
            diff = abs(sf_rows - lw_rows)
            if diff <= tolerance:
                result = "PASS"
                details = f"Row count match (SF={sf_rows}, LAWEB={lw_rows}, diff={diff}, tol={tolerance})."
            else:
                result = "FAIL"
                details = f"Row count mismatch (SF={sf_rows}, LAWEB={lw_rows}, diff={diff})."

        elif r_type == "missing_ids":
            if len(ids_sf_only) == 0:
                result = "PASS"
                details = "No IDs missing in LAWEB."
            else:
                result = "FAIL"
                details = f"{len(ids_sf_only)} IDs present in SF but missing in LAWEB."

        elif r_type == "extra_ids":
            if len(ids_laweb_only) == 0:
                result = "PASS"
                details = "No extra IDs in LAWEB."
            else:
                result = "FAIL"
                details = f"{len(ids_laweb_only)} IDs present in LAWEB but missing in SF."

        elif r_type == "column_count":
            if sf_cols == lw_cols:
                result = "PASS"
                details = f"Column counts match (SF={sf_cols}, LAWEB={lw_cols})."
            else:
                result = "FAIL"
                details = f"Column counts differ (SF={sf_cols}, LAWEB={lw_cols})."

        elif r_type == "column_names":
            if not column_missing_sf and not column_missing_laweb:
                result = "PASS"
                details = "All column names match."
            else:
                result = "FAIL"
                details = (
                    f"Missing in SF: {len(column_missing_sf)}, "
                    f"missing in LAWEB: {len(column_missing_laweb)}."
                )

        elif r_type == "pk_unique":
            sf_dup = sf[pk].duplicated(keep=False).sum()
            lw_dup = laweb[pk].duplicated(keep=False).sum()
            if sf_dup == 0 and lw_dup == 0:
                result = "PASS"
                details = "Primary key is unique in both datasets."
            else:
                result = "FAIL"
                details = f"Duplicate PK values - SF={sf_dup}, LAWEB={lw_dup}."

        elif r_type == "pk_not_null":
            sf_null = sf[pk].isna().sum()
            lw_null = laweb[pk].isna().sum()
            if sf_null == 0 and lw_null == 0:
                result = "PASS"
                details = "Primary key has no NULL values in both datasets."
            else:
                result = "FAIL"
                details = f"NULL PK values - SF={sf_null}, LAWEB={lw_null}."

        elif r_type == "sample_row_compare":
            if row_diff is None or row_diff.empty:
                result = "PASS"
                details = "No row-level mismatches detected in sample."
            else:
                result = "FAIL"
                details = f"{len(row_diff)} row-level mismatches detected (sample, max 100 shown)."

        elif r_type == "full_row_compare":
            if full_mismatch_count is None:
                full_mismatch_count = _compute_full_row_mismatch_count(sf, laweb, pk, common_cols)
            if full_mismatch_count == 0:
                result = "PASS"
                details = "All matched rows are identical across all common columns."
            else:
                result = "FAIL"
                details = f"{full_mismatch_count} joined rows have at least one differing column value."

        elif r_type == "null_pattern":
            threshold = float(rule_def.get("threshold", 20.0))
            if null_pattern_cache is None:
                null_pattern_cache = _compute_null_pattern_violations(sf, laweb, common_cols, threshold)
            if not null_pattern_cache:
                result = "PASS"
                details = f"NULL pattern consistent within ±{threshold}% for all common columns."
            else:
                result = "FAIL"
                top = null_pattern_cache[:3]
                sample_str = ", ".join(
                    f"{v['column']} (SF={v['sf_null_pct']}%, LAWEB={v['laweb_null_pct']}%, Δ={v['diff_pct']}%)"
                    for v in top
                )
                details = (
                    f"NULL pattern differs by more than {threshold}% in "
                    f"{len(null_pattern_cache)} columns. Top examples: {sample_str}"
                )

        else:
            result = "SKIPPED"
            details = f"Unknown or not implemented rule type '{r_type}'."

        # -------------- SCORING --------------
        if result == "PASS":
            passed += 1
            total_weight += weight
            gained_weight += weight
        elif result == "FAIL":
            failed += 1
            total_weight += weight
            if priority.strip().lower() == "critical":
                critical_failed += 1
        else:
            skipped += 1

        results.append(
            {
                "id": rule_id,
                "name": name,
                "priority": priority,
                "result": result,
                "details": details,
            }
        )

    score = 100.0 if total_weight == 0 else round(100.0 * gained_weight / total_weight, 2)

    return {
        "score": score,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "critical_failed": critical_failed,
        "rules": results,
    }
