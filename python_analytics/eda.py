# =============================================================================
# eda.py — Hospital Analytics Pipeline: Exploratory Data Analysis
# =============================================================================
# All data quality checks, cleaning, and normalization live here.
# Functions return cleaned DataFrames and print a human-readable report.
# =============================================================================

import re
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Null / Missing Value Audit
# ─────────────────────────────────────────────────────────────────────────────

def check_nulls(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Check every table for null values.

    Args:
        dfs: dict of raw DataFrames (output of load_raw_tables)

    Returns:
        summary DataFrame: table | column | null_count | null_pct
    """
    rows = []
    for table_name, df in dfs.items():
        for col in df.columns:
            null_count = df[col].isna().sum()
            null_pct   = round(null_count / len(df) * 100, 2)
            rows.append({
                "table":      table_name,
                "column":     col,
                "null_count": null_count,
                "null_pct":   null_pct,
            })

    summary = pd.DataFrame(rows)
    total_nulls = summary["null_count"].sum()

    print("=" * 60)
    print("NULL / MISSING VALUE AUDIT")
    print("=" * 60)
    if total_nulls == 0:
        print("[OK]  No null values found across all 7 tables.")
    else:
        flagged = summary[summary["null_count"] > 0]
        print(f"[!!]  Found {total_nulls} null value(s) in "
              f"{len(flagged)} column(s):\n")
        print(flagged.to_string(index=False))
    print()

    return summary


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Duplicate Patient Detection
# ─────────────────────────────────────────────────────────────────────────────

def check_duplicate_patients(patient_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect patients with identical (name, surname) — possible duplicates.
    Note: same name ≠ guaranteed duplicate (e.g. Patient 1 and 5 are both
    "John Smith" but have different addresses → distinct people).

    Returns:
        DataFrame of rows where (name, surname) appears more than once.
    """
    print("=" * 60)
    print("DUPLICATE PATIENT NAME DETECTION")
    print("=" * 60)

    dupes = patient_df[
        patient_df.duplicated(subset=["name", "surname"], keep=False)
    ].copy()

    if dupes.empty:
        print("[OK]  No duplicate (name, surname) combinations found.")
    else:
        print(f"[!!]  {len(dupes)} rows share a (name, surname) -- "
              f"verify these are distinct patients:\n")
        print(dupes[["patient_id", "name", "surname", "address",
                      "gender", "phone"]].to_string(index=False))
        print("\nNote: Different addresses/phones confirm distinct people.")
    print()

    return dupes


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Gender Normalization
# ─────────────────────────────────────────────────────────────────────────────

def normalize_gender(patient_df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize the gender column to Title Case ('Male', 'Female').
    The raw data contains mixed-case variants ('MALE', 'male', etc.).

    Returns:
        patient_df with normalized gender column (in-place copy).
    """
    df = patient_df.copy()
    before = df["gender"].value_counts().to_dict()
    df["gender"] = df["gender"].str.strip().str.title()
    after  = df["gender"].value_counts().to_dict()

    print("=" * 60)
    print("GENDER NORMALIZATION")
    print("=" * 60)
    print(f"  Before: {before}")
    print(f"  After:  {after}")
    unexpected = set(df["gender"].unique()) - {"Male", "Female"}
    if unexpected:
        print(f"  [!!] Unexpected values found: {unexpected}")
    else:
        print("  [OK] All values normalized to Male / Female.")
    print()

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Phone Format Check
# ─────────────────────────────────────────────────────────────────────────────

# Expected formats observed in data: '555-0256-896', '555-123-4567'
# Both are valid fiction numbers — just flag anything non-numeric/dash.
_PHONE_RE = re.compile(r"^\d{3}-\d{3,4}-\d{3,4}$")


def check_phone_formats(patient_df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag any phone values that don't match the expected '###-###-####' pattern.

    Returns:
        DataFrame of rows with non-standard phone values (empty if all OK).
    """
    print("=" * 60)
    print("PHONE FORMAT VALIDATION")
    print("=" * 60)

    flagged = patient_df[
        ~patient_df["phone"].astype(str).str.match(_PHONE_RE)
    ]

    if flagged.empty:
        print("[OK]  All phone numbers match expected format.")
    else:
        print(f"[!!]  {len(flagged)} non-standard phone number(s):\n")
        print(flagged[["patient_id", "name", "surname", "phone"]]
              .to_string(index=False))
    print()

    return flagged


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Data Type Audit
# ─────────────────────────────────────────────────────────────────────────────

def audit_dtypes(dfs: dict[str, pd.DataFrame]) -> None:
    """
    Print dtypes for all tables to confirm numeric columns loaded correctly
    (e.g. cost as int, not object).
    """
    print("=" * 60)
    print("DATA TYPE AUDIT")
    print("=" * 60)

    issues = []
    expected_numeric = {
        "physician":         ["employeeid"],
        "department":        ["department_id", "head"],
        "affiliated_with":   ["physicianid", "departmentid"],
        "nurse":             ["nurse_id"],
        "patient":           ["patient_id", "primary_check"],
        "patient_diagnosis": ["patient_id", "physician_id"],
        "procedures":        ["code", "cost"],
    }

    for table, cols in expected_numeric.items():
        df = dfs.get(table)
        if df is None:
            continue
        for col in cols:
            if col not in df.columns:
                continue
            if not pd.api.types.is_numeric_dtype(df[col]):
                issues.append(f"  [!!] {table}.{col} -> dtype={df[col].dtype} (expected numeric)")

    if issues:
        print("\n".join(issues))
    else:
        print("[OK]  All expected numeric columns loaded with correct dtypes.")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# 6.  Procedure Cost Statistics
# ─────────────────────────────────────────────────────────────────────────────

def summarize_procedure_costs(procedures_df: pd.DataFrame) -> pd.DataFrame:
    """
    Descriptive statistics for the procedure cost catalog.

    Returns:
        DataFrame with min, max, mean, median, std for cost column.
    """
    print("=" * 60)
    print("PROCEDURE COST — DESCRIPTIVE STATISTICS")
    print("=" * 60)

    stats = procedures_df["cost"].describe().rename({
        "count": "count",
        "mean":  "mean (avg)",
        "std":   "std dev",
        "min":   "minimum",
        "25%":   "25th pct",
        "50%":   "median",
        "75%":   "75th pct",
        "max":   "maximum",
    })

    print(stats.to_string())
    print()

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# 7.  Address Street-Type Extraction (geographic proxy)
# ─────────────────────────────────────────────────────────────────────────────

# Known suffixes in the dataset; catches: St, Ave, Dr, Lane, Drive, Street, etc.
_SUFFIX_RE = re.compile(
    r"\b(Street|St|Avenue|Ave|Drive|Dr|Lane|Ln|Road|Rd|Blvd|Boulevard|"
    r"Court|Ct|Place|Pl|Way|Terrace|Terr)\b",
    re.IGNORECASE,
)


def extract_street_type(patient_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the street type (suffix) from address strings as a geographic proxy.
    Real city/state data doesn't exist in the schema — this is the best we can do.

    Returns:
        patient_df with a new 'street_type' column added.
    """
    df = patient_df.copy()

    def _extract(addr: str) -> str:
        m = _SUFFIX_RE.search(str(addr))
        if m:
            # Normalise variants: 'St' and 'Street' → 'St'
            raw = m.group(1).title()
            return {
                "Street": "St", "Avenue": "Ave", "Drive": "Dr",
                "Lane": "Ln", "Road": "Rd", "Boulevard": "Blvd",
                "Court": "Ct", "Place": "Pl", "Terrace": "Terr",
            }.get(raw, raw)
        return "Unknown"

    df["street_type"] = df["address"].apply(_extract)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 8.  Master EDA Runner
# ─────────────────────────────────────────────────────────────────────────────

def run_full_eda(dfs: dict[str, pd.DataFrame]) -> dict:
    """
    Run the complete EDA pipeline on all raw tables.

    Returns:
        results dict with cleaned DataFrames and summary tables:
            - null_summary
            - duplicate_patients
            - phone_issues
            - patient_df         (cleaned: gender normalized + street_type)
            - procedure_stats
    """
    print("  [1] EDA STARTED")
    print("  HOSPITAL ANALYTICS -- EDA REPORT")
    print("[" + "=" * 58 + "]" + "\n")

    null_summary       = check_nulls(dfs)
    duplicate_patients = check_duplicate_patients(dfs["patient"])
    patient_cleaned    = normalize_gender(dfs["patient"])
    phone_issues       = check_phone_formats(patient_cleaned)
    audit_dtypes(dfs)
    procedure_stats    = summarize_procedure_costs(dfs["procedures"])
    patient_cleaned    = extract_street_type(patient_cleaned)

    print("[" + "=" * 58 + "]")
    print("  EDA COMPLETE")
    print("[" + "=" * 58 + "]" + "\n")

    return {
        "null_summary":       null_summary,
        "duplicate_patients": duplicate_patients,
        "phone_issues":       phone_issues,
        "patient_cleaned":    patient_cleaned,
        "procedure_stats":    procedure_stats,
    }
