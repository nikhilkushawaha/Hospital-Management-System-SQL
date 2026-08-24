# =============================================================================
# data_loader.py — Hospital Analytics Pipeline: Data Loading & Merging
# =============================================================================
# Responsibilities:
#   1. get_engine()       → SQLAlchemy engine for MySQL or SQLite
#   2. load_raw_tables()  → Dict of raw DataFrames, one per table
#   3. build_master_df()  → Merged DataFrame ready for analysis
# =============================================================================

import os
import pandas as pd
from config import DATA_SOURCE, MYSQL_CONFIG, DATA_DIR


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Engine / Connection
# ─────────────────────────────────────────────────────────────────────────────

def get_engine():
    """
    Return a SQLAlchemy engine.

    • DATA_SOURCE = "mysql"  →  connects to live MySQL using MYSQL_CONFIG
    • DATA_SOURCE = "csv"    →  returns None (CSV path used directly)

    The engine abstraction means swapping MySQL ↔ SQLite is a one-liner.
    """
    if DATA_SOURCE == "mysql":
        try:
            from sqlalchemy import create_engine
            cfg = MYSQL_CONFIG
            url = (
                f"mysql+mysqlconnector://{cfg['user']}:{cfg['password']}"
                f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
            )
            engine = create_engine(url, echo=False)
            # Lightweight connection test
            with engine.connect():
                pass
            print(f"[data_loader] OK  Connected to MySQL: {cfg['database']}@{cfg['host']}")
            return engine
        except Exception as exc:
            raise ConnectionError(
                f"[data_loader] ERROR  Could not connect to MySQL.\n"
                f"  Check MYSQL_CONFIG in config.py.\n"
                f"  Error: {exc}"
            )
    # CSV mode — no engine needed
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Raw Table Loading
# ─────────────────────────────────────────────────────────────────────────────

# Map: logical name → (csv filename, SQL table name)
TABLE_MAP = {
    "physician":        ("physician.csv",        "Physician"),
    "department":       ("department.csv",        "department"),
    "affiliated_with":  ("affiliated_with.csv",   "affiliated_with"),
    "nurse":            ("nurse.csv",             "Nurse"),
    "patient":          ("patient.csv",           "Patient"),
    "patient_diagnosis":("patient_diagnosis.csv", "PATIENT_DIAGNOSIS"),
    "procedures":       ("procedures.csv",        "procedures"),
}


def load_raw_tables(engine=None) -> dict[str, pd.DataFrame]:
    """
    Load all 7 hospital tables into a dict of DataFrames.

    Args:
        engine: SQLAlchemy engine (required for MySQL mode, None for CSV mode)

    Returns:
        dict with keys: physician, department, affiliated_with, nurse,
                        patient, patient_diagnosis, procedures
    """
    dfs = {}

    for name, (csv_file, sql_table) in TABLE_MAP.items():
        if DATA_SOURCE == "csv":
            path = os.path.join(DATA_DIR, csv_file)
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"[data_loader] CSV not found: {path}\n"
                    f"  Run export_to_csv.py first, or set DATA_SOURCE='mysql'."
                )
            dfs[name] = pd.read_csv(path)
            print(f"[data_loader] CSV  Loaded '{name}' from CSV  "
                  f"({len(dfs[name])} rows)")

        elif DATA_SOURCE == "mysql":
            if engine is None:
                raise ValueError("engine must be provided when DATA_SOURCE='mysql'")
            dfs[name] = pd.read_sql(f"SELECT * FROM {sql_table}", con=engine)
            print(f"[data_loader] DB   Loaded '{name}' from MySQL "
                  f"({len(dfs[name])} rows)")

        else:
            raise ValueError(
                f"Invalid DATA_SOURCE='{DATA_SOURCE}'. "
                f"Must be 'csv' or 'mysql'."
            )

    return dfs


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Master (Merged) DataFrame
# ─────────────────────────────────────────────────────────────────────────────

def build_master_df(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Build a wide, analysis-ready DataFrame by joining the core tables.

    Join chain:
        patient_diagnosis
          LEFT JOIN physician     ON physician_id  = employeeid
          LEFT JOIN patient       ON patient_id    = patient_id
          LEFT JOIN affiliated_with (primary only) ON employeeid = physicianid
          LEFT JOIN department    ON departmentid  = department_id

    Returns:
        master_df — one row per patient–diagnosis record, enriched with
        physician name/position, patient demographics, and department name.

    Schema note: `procedures` is a standalone cost catalog and is NOT
    joined here (no patient_procedure junction table exists in the schema).
    Procedure analysis is kept separate — see insights.py.
    """
    pd_df  = dfs["patient_diagnosis"].copy()
    phy_df = dfs["physician"].copy()
    pat_df = dfs["patient"].copy()
    aff_df = dfs["affiliated_with"].copy()
    dep_df = dfs["department"].copy()

    # ── Rename ambiguous columns before merging ───────────────────────────
    phy_df = phy_df.rename(columns={
        "employeeid": "physician_employeeid",
        "name":       "physician_name",
        "position":   "physician_position",
    })

    pat_df = pat_df.rename(columns={
        "name":    "patient_first_name",
        "surname": "patient_surname",
    })
    pat_df["patient_full_name"] = (
        pat_df["patient_first_name"] + " " + pat_df["patient_surname"]
    )

    dep_df = dep_df.rename(columns={"dept_name": "department_name"})

    # ── Physician's PRIMARY department affiliation only ───────────────────
    primary_aff = aff_df[aff_df["primaryaffiliation"] == "t"][
        ["physicianid", "departmentid"]
    ].drop_duplicates(subset="physicianid")   # one row per physician

    # ── Join chain ────────────────────────────────────────────────────────
    master = (
        pd_df
        # Add physician details
        .merge(
            phy_df[["physician_employeeid", "physician_name", "physician_position"]],
            left_on="physician_id",
            right_on="physician_employeeid",
            how="left",
        )
        # Add patient details
        .merge(
            pat_df[[
                "patient_id", "patient_full_name", "patient_first_name",
                "patient_surname", "address", "gender", "phone", "primary_check"
            ]],
            on="patient_id",
            how="left",
        )
        # Add primary department affiliation
        .merge(
            primary_aff.rename(columns={"departmentid": "department_id"}),
            left_on="physician_id",
            right_on="physicianid",
            how="left",
        )
        # Add department name
        .merge(
            dep_df[["department_id", "department_name"]],
            on="department_id",
            how="left",
        )
    )

    # ── Drop redundant key columns ────────────────────────────────────────
    master = master.drop(
        columns=["physician_employeeid", "physicianid"],
        errors="ignore",
    )

    print(f"[data_loader] JOIN  master_df built -- {master.shape[0]} rows x "
          f"{master.shape[1]} columns")
    return master


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Convenience: load everything in one call
# ─────────────────────────────────────────────────────────────────────────────

def load_all() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """
    One-shot helper used by the notebook:
        dfs, master = load_all()

    Returns:
        dfs    — dict of raw DataFrames (all 7 tables)
        master — merged analysis-ready DataFrame
    """
    engine = get_engine()
    dfs = load_raw_tables(engine)
    master = build_master_df(dfs)
    return dfs, master
