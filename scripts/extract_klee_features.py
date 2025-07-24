import os
import csv
import sqlite3
import logging
from pathlib import Path

# --- Configuration ---
# The script will look for klee-out-* folders inside this directory.

RESULTS_DIR = Path("results")
OUTPUT_CSV = RESULTS_DIR / "klee_features_rich_gurman.csv"
KLEE_OUT_PREFIX = "klee-out-"

# --- Setup logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

FEATURE_COLUMNS = [
    "Instructions", "FullBranches", "PartialBranches", "NumBranches",
    "SolverQueries", "NumQueryConstructs", "CoveredInstructions",
    "UncoveredInstructions", "UserTime", "Allocations", "ExternalCalls"
]

def extract_stats(klee_out_dir):
    """Extracts performance stats from the run.stats SQLite file."""
    stats_file = klee_out_dir / "run.stats"
    warnings_file = klee_out_dir / "warnings.txt"

    stats = {key: 0 for key in FEATURE_COLUMNS}
    warnings_count = 0
    
    if stats_file.exists():
        try:
            conn = sqlite3.connect(stats_file)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cur.fetchall()]
            if "stats" in tables:
                cur.execute("PRAGMA table_info(stats);")
                available_columns = [row[1] for row in cur.fetchall()]
                selected = [col for col in FEATURE_COLUMNS if col in available_columns]
                if selected:
                    query = f"SELECT {', '.join(selected)} FROM stats LIMIT 1;"
                    cur.execute(query)
                    row = cur.fetchone()
                    if row:
                        for i, col in enumerate(selected):
                            stats[col] = row[i] if row[i] is not None else 0
            conn.close()
        except Exception as e:
            logging.warning(f"Failed to read stats from {stats_file}: {e}")

    if warnings_file.exists():
        try:
            with open(warnings_file, "r") as f:
                warnings_count = sum(1 for line in f if line.strip().startswith("KLEE: WARNING"))
        except Exception as e:
            logging.warning(f"Failed to read warnings from {warnings_file}: {e}")

    return (*[stats[key] for key in FEATURE_COLUMNS], warnings_count)

def collect_klee_outputs():
    """Finds all directories starting with 'klee-out-'."""
    logging.info(f"Scanning for KLEE output directories in '{RESULTS_DIR}'...")
    out_dirs = sorted([d for d in RESULTS_DIR.iterdir() if d.is_dir() and d.name.startswith(KLEE_OUT_PREFIX)])
    logging.info(f"Found {len(out_dirs)} KLEE output directories.")
    return out_dirs

# --- NEW AND IMPROVED FUNCTION TO GET NAME AND LABEL ---
def extract_info_and_label(klee_out_dir):
    """
    Reads the 'info' file inside a klee-out directory to find the
    original function name and determine its label (good/bad).
    """
    info_file = klee_out_dir / "info"
    function_name = "unknown"
    label = -1  # Default to -1 (unknown)

    if not info_file.exists():
        logging.warning(f"Missing 'info' file in {klee_out_dir}")
        return function_name, label

    try:
        with open(info_file, "r") as f:
            first_line = f.readline()
            # Line is like: klee --libc=uclibc ../results/CWE190..._good.bc
            # We want the last part of that line.
            parts = first_line.strip().split(' ')
            bitcode_path = Path(parts[-1])
            
            # Get filename without the '.bc' extension
            function_name = bitcode_path.stem

            # Determine label from the filename
            if "_bad" in function_name:
                label = 1  # Vulnerable
            elif "_good" in function_name:
                label = 0  # Not vulnerable
            else:
                logging.warning(f"Could not determine label from name: {function_name}")

    except Exception as e:
        logging.error(f"Failed to read or parse {info_file}: {e}")

    return function_name, label

def main():
    out_dirs = collect_klee_outputs()
    if not out_dirs:
        logging.error("No KLEE output directories found. Exiting.")
        return

    # Use a more descriptive header
    header = ["klee_dir_name", "function_name"] + FEATURE_COLUMNS + ["warnings", "label"]
    features = [header]

    for klee_dir in out_dirs:
        # Get function name and label from the 'info' file
        function_name, label = extract_info_and_label(klee_dir)
        
        # Get the KLEE execution stats
        stat_values = extract_stats(klee_dir)
        
        # Add the full row to our data
        features.append((klee_dir.name, function_name, *stat_values, label))

    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(features)

    logging.info(f"✅ Feature extraction complete. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()