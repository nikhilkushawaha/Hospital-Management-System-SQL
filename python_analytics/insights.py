# =============================================================================
# insights.py — Hospital Analytics Pipeline: Analytical Insights
# =============================================================================
# All business-logic analytics functions live here.
# Each function takes DataFrames and returns a result DataFrame + prints a
# formatted summary so it can be used both in notebooks and scripts.
# =============================================================================

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Diagnosis Frequency
# ─────────────────────────────────────────────────────────────────────────────

def diagnosis_frequency(master_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Most common diagnoses across all patients.

    Args:
        master_df: merged DataFrame from data_loader.build_master_df()
        top_n:     number of top diagnoses to return

    Returns:
        DataFrame with columns: diagnosis | count | pct_of_patients
    """
    total = len(master_df)
    freq = (
        master_df["diagnosis"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "count"})
        .head(top_n)
    )
    freq["pct_of_patients"] = (freq["count"] / total * 100).round(1)

    print("=" * 60)
    print(f"TOP {top_n} DIAGNOSES (all patients)")
    print("=" * 60)
    print(freq.to_string(index=False))
    print()

    return freq


def diagnosis_by_physician(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Number of diagnoses handled per physician, ranked descending.

    Returns:
        DataFrame: physician_name | physician_position | diagnosis_count
    """
    result = (
        master_df.groupby(["physician_name", "physician_position"])
        .size()
        .reset_index(name="diagnosis_count")
        .sort_values("diagnosis_count", ascending=False)
        .reset_index(drop=True)
    )

    print("=" * 60)
    print("DIAGNOSIS COUNT BY PHYSICIAN (ranked)")
    print("=" * 60)
    print(result.to_string(index=False))
    print()

    return result


def diagnosis_by_department(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Number of diagnoses handled per department (via physician's primary affiliation).

    Returns:
        DataFrame: department_name | diagnosis_count
    """
    result = (
        master_df.groupby("department_name")
        .size()
        .reset_index(name="diagnosis_count")
        .sort_values("diagnosis_count", ascending=False)
        .reset_index(drop=True)
    )

    # Handle unaffiliated rows
    result["department_name"] = result["department_name"].fillna("Unaffiliated")

    print("=" * 60)
    print("DIAGNOSIS COUNT BY DEPARTMENT")
    print("=" * 60)
    print(result.to_string(index=False))
    print()

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Physician Workload
# ─────────────────────────────────────────────────────────────────────────────

def physician_patient_count(patient_df: pd.DataFrame,
                             physician_df: pd.DataFrame) -> pd.DataFrame:
    """
    Number of patients per primary physician (from patient.primary_check).
    This is distinct from diagnoses: a physician may have primary care of
    multiple patients without personally diagnosing all of them.

    Returns:
        DataFrame: physician_name | patient_count
    """
    merged = patient_df.merge(
        physician_df.rename(columns={
            "employeeid": "primary_check",
            "name": "physician_name",
        }),
        on="primary_check",
        how="left",
    )

    result = (
        merged.groupby("physician_name")
        .size()
        .reset_index(name="patient_count")
        .sort_values("patient_count", ascending=False)
        .reset_index(drop=True)
    )

    print("=" * 60)
    print("PATIENTS PER PRIMARY PHYSICIAN (ranked)")
    print("=" * 60)
    print(result.to_string(index=False))
    print()

    return result


def physician_workload_combined(master_df: pd.DataFrame,
                                 patient_df: pd.DataFrame,
                                 physician_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combined workload table: diagnoses handled + patients under primary care.

    Returns:
        DataFrame: physician_name | diagnoses_handled | primary_patients
    """
    diag = diagnosis_by_physician(master_df)[
        ["physician_name", "diagnosis_count"]
    ].rename(columns={"diagnosis_count": "diagnoses_handled"})

    primary = physician_patient_count(patient_df, physician_df)[
        ["physician_name", "patient_count"]
    ].rename(columns={"patient_count": "primary_patients"})

    result = diag.merge(primary, on="physician_name", how="outer").fillna(0)
    result["diagnoses_handled"] = result["diagnoses_handled"].astype(int)
    result["primary_patients"]  = result["primary_patients"].astype(int)
    result = result.sort_values("diagnoses_handled", ascending=False).reset_index(drop=True)

    print("=" * 60)
    print("COMBINED PHYSICIAN WORKLOAD")
    print("=" * 60)
    print(result.to_string(index=False))
    print()

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Procedure Cost Analysis
# ─────────────────────────────────────────────────────────────────────────────

def procedure_cost_by_name(procedures_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cost breakdown per procedure name (sorted by cost descending).
    Since each procedure code maps 1:1 to a name and cost, this is essentially
    a sorted catalog — useful as a reference and for visualization.

    Schema note: No patient_procedure junction table exists, so we cannot
    compute "total cost incurred by patients" — only the catalog price.

    Returns:
        DataFrame: name | cost | cost_pct_of_max
    """
    df = procedures_df[["name", "cost"]].sort_values("cost", ascending=False).copy()
    df["cost_pct_of_max"] = (df["cost"] / df["cost"].max() * 100).round(1)
    df = df.reset_index(drop=True)

    print("=" * 60)
    print("PROCEDURE COST CATALOG (sorted by cost, descending)")
    print("⚠️  Note: No patient_procedure table — catalog prices only")
    print("=" * 60)
    print(df.to_string(index=False))
    print()

    return df


def procedure_cost_stats(procedures_df: pd.DataFrame) -> dict:
    """
    Summary statistics for the procedure cost column.

    Returns:
        dict with overall mean, median, std, min, max
    """
    cost = procedures_df["cost"]
    stats = {
        "mean":   round(cost.mean(), 2),
        "median": round(cost.median(), 2),
        "std":    round(cost.std(), 2),
        "min":    int(cost.min()),
        "max":    int(cost.max()),
        "count":  int(cost.count()),
    }

    print("=" * 60)
    print("PROCEDURE COST — KEY STATISTICS")
    print("=" * 60)
    for k, v in stats.items():
        label = k.ljust(8)
        print(f"  {label}: {v:>10,}")
    print()

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Patient Demographics
# ─────────────────────────────────────────────────────────────────────────────

def gender_distribution(patient_df: pd.DataFrame) -> pd.DataFrame:
    """
    Gender split across all patients.

    Args:
        patient_df: cleaned patient DataFrame (gender already normalized)

    Returns:
        DataFrame: gender | count | percentage
    """
    result = (
        patient_df["gender"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "count"})
    )
    result["percentage"] = (result["count"] / result["count"].sum() * 100).round(1)

    print("=" * 60)
    print("PATIENT GENDER DISTRIBUTION")
    print("=" * 60)
    print(result.to_string(index=False))
    print()

    return result


def street_type_distribution(patient_df: pd.DataFrame) -> pd.DataFrame:
    """
    Distribution of address street types (geographic proxy).
    Real city/state data is absent from the schema — street suffix is the
    only geographic dimension available.

    Args:
        patient_df: patient DataFrame with 'street_type' column (from eda.py)

    Returns:
        DataFrame: street_type | count | percentage
    """
    if "street_type" not in patient_df.columns:
        raise ValueError(
            "patient_df must have 'street_type' column. "
            "Run eda.extract_street_type() first."
        )

    result = (
        patient_df["street_type"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "count"})
    )
    result["percentage"] = (result["count"] / result["count"].sum() * 100).round(1)

    print("=" * 60)
    print("ADDRESS STREET-TYPE DISTRIBUTION (geographic proxy)")
    print("⚠️  Note: No city/state field — street suffix is the only available")
    print("   geographic dimension. Schema limitation flagged.")
    print("=" * 60)
    print(result.to_string(index=False))
    print()

    return result


def nurse_registration_stats(nurse_df: pd.DataFrame) -> dict:
    """
    Registered vs unregistered nurse breakdown, by position.

    Returns:
        dict with overall counts and position-level crosstab.
    """
    overall = nurse_df["registered"].value_counts().to_dict()
    crosstab = pd.crosstab(nurse_df["position"], nurse_df["registered"])

    print("=" * 60)
    print("NURSE REGISTRATION STATISTICS")
    print("=" * 60)
    print(f"  Overall: {overall}")
    print("\n  By position:\n")
    print(crosstab.to_string())
    print()

    return {"overall": overall, "by_position": crosstab}


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Schema Limitation Summary
# ─────────────────────────────────────────────────────────────────────────────

def print_schema_limitations() -> None:
    """
    Print a clear summary of schema limitations that prevent certain analyses.
    Included here so it can be called in the notebook as a documented section.
    """
    print("=" * 60)
    print("SCHEMA LIMITATION NOTES")
    print("=" * 60)
    limitations = [
        ("Age / DOB distribution",
         "No date_of_birth or age column in Patient table.\n"
         "   Insight is not computable. Schema change required: ADD COLUMN dob DATE."),

        ("Department-level cost analysis",
         "No patient_procedure junction table linking patients to procedures.\n"
         "   The 'procedures' table is a standalone cost catalog.\n"
         "   Insight is not computable. Schema change required:\n"
         "   CREATE TABLE patient_procedure (patient_id, procedure_code, date)."),

        ("Geographic distribution",
         "Patient.address contains raw street strings (no city/state/ZIP).\n"
         "   True geographic distribution is not computable.\n"
         "   We use street-type suffix as a proxy (St, Ave, Dr, etc.)."),
    ]

    for i, (title, detail) in enumerate(limitations, 1):
        print(f"\n  [{i}] ❌  {title}")
        print(f"       {detail}")

    print()
