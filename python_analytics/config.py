# =============================================================================
# config.py — Hospital Analytics Pipeline Configuration
# =============================================================================
# Toggle DATA_SOURCE to switch between live MySQL and offline CSV mode.
# For portfolio demo / anyone without a MySQL server: leave as "csv".
# For live DB queries: set to "mysql" and fill in your credentials below.
# =============================================================================

# ── Data source ───────────────────────────────────────────────────────────────
# Options: "csv" | "mysql"
DATA_SOURCE = "csv"

# ── MySQL connection settings (only used when DATA_SOURCE = "mysql") ──────────
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",          # ← replace with your MySQL username
    "password": "",          # ← replace with your MySQL password
    "database": "HOSPITAL_MANAGMENT_SYSTEM",  # matches the SQL file
}

# ── File paths ────────────────────────────────────────────────────────────────
import os

# Base directory: folder containing this config file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder containing pre-exported CSVs
DATA_DIR = os.path.join(BASE_DIR, "data")

# Folder where chart PNGs will be saved
VISUALS_DIR = os.path.join(BASE_DIR, "visuals")

# ── Chart settings ────────────────────────────────────────────────────────────
FIGURE_DPI = 150          # resolution for saved PNGs
FIGURE_STYLE = "seaborn-v0_8-whitegrid"   # matplotlib style
COLOR_PALETTE = "husl"    # seaborn palette used across charts
