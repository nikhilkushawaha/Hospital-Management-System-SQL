# =============================================================================
# export_to_csv.py — Hospital Analytics Pipeline: MySQL → CSV Exporter
# =============================================================================
# One-time script: connects to live MySQL and dumps all 7 tables to CSV.
# Run this once, then set DATA_SOURCE = "csv" in config.py for offline use.
#
# Usage:
#   cd python_analytics
#   python export_to_csv.py
# =============================================================================

import os
import pandas as pd

# Ensure we can import config from the same directory
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MYSQL_CONFIG, DATA_DIR
from data_loader import get_engine, TABLE_MAP


def export_all_tables_to_csv() -> None:
    """
    Connect to MySQL and export every table in TABLE_MAP to a CSV file
    in the /data directory.
    """
    print("=" * 60)
    print("HOSPITAL DB — MySQL → CSV EXPORT")
    print("=" * 60)
    print(f"  Target directory: {DATA_DIR}\n")

    # Temporarily override DATA_SOURCE to 'mysql' for this script
    import config
    original_source = config.DATA_SOURCE
    config.DATA_SOURCE = "mysql"

    try:
        engine = get_engine()
    except ConnectionError as e:
        print(e)
        print("\n  ❌  Export aborted. Check MYSQL_CONFIG in config.py.")
        return
    finally:
        config.DATA_SOURCE = original_source

    os.makedirs(DATA_DIR, exist_ok=True)

    for name, (csv_file, sql_table) in TABLE_MAP.items():
        try:
            df = pd.read_sql(f"SELECT * FROM {sql_table}", con=engine)
            out_path = os.path.join(DATA_DIR, csv_file)
            df.to_csv(out_path, index=False)
            print(f"  ✅  {sql_table:<25} → {csv_file}  ({len(df)} rows)")
        except Exception as exc:
            print(f"  ❌  Failed to export '{sql_table}': {exc}")

    print("\n  Export complete. Set DATA_SOURCE = 'csv' in config.py to use offline.")
    print("=" * 60)


if __name__ == "__main__":
    export_all_tables_to_csv()
