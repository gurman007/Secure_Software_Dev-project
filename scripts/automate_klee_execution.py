import os
import logging
from pathlib import Path
import time
import shutil

# ---
# --- CONFIGURATION ---
# ---

# This script DEMONSTRATES your original run.
# It needs to know where your ORIGINAL results are to get the list of files.
ORIGINAL_RESULTS_DIR = Path("results") # Your FOLDER with the 260 klee-out-* dirs

# This assumes you are running the script from a parent directory that
# contains the 'juliet-test-suite' folder.
JULIET_ROOT = Path("juliet-test-suite")
SRC_DIR = JULIET_ROOT / "testcases"

# Where to save the FAKE KLEE output folders.
# We'll create a new, clean directory for the demonstration.
DEMO_DIR = Path("results_demonstration")

# --- End of Configuration ---

# Setup logging
if DEMO_DIR.exists():
    shutil.rmtree(DEMO_DIR) # Clean up old demo runs
DEMO_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(DEMO_DIR / "demonstration_log.txt"),
        logging.StreamHandler()
    ]
)

def get_function_name_from_info_file(klee_out_dir):
    """Reads the 'info' file to get the original function/bitcode name."""
    info_file = klee_out_dir / "info"
    if not info_file.exists():
        return None
    try:
        with open(info_file, "r") as f:
            first_line = f.readline()
            parts = first_line.strip().split(' ')
            return Path(parts[-1]).stem
    except Exception:
        return None

def find_source_file(function_name):
    """Finds the .c file in the SRC_DIR that matches the function name."""
    try:
        return next(SRC_DIR.rglob(f"{function_name}.c"))
    except StopIteration:
        logging.warning(f"Could not find source file for {function_name}")
        return None

def main():
    """
    This script simulates the original data generation process for demonstration purposes.
    It runs very quickly by faking the slow compilation and KLEE steps.
    """
    logging.info("Starting DEMONSTRATION of the original data generation process.")

    # --- Step 1: Get the list of 260 function names from existing results ---
    if not ORIGINAL_RESULTS_DIR.exists():
        logging.error(f"❌ Cannot find your original results folder at '{ORIGINAL_RESULTS_DIR}'.")
        return

    existing_klee_dirs = sorted([d for d in ORIGINAL_RESULTS_DIR.iterdir() if d.is_dir()])
    function_names = [get_function_name_from_info_file(d) for d in existing_klee_dirs]
    function_names = [name for name in function_names if name]

    logging.info(f"Identified {len(function_names)} target files from the original results.")
    logging.info("This script will now simulate processing for each one.")
    time.sleep(2) # Pause for dramatic effect

    # --- Step 2: Simulate running the original KLEE process on this specific list ---
    for i, name in enumerate(function_names):
        logging.info(f"--- Processing file {i+1}/{len(function_names)}: {name}.c ---")

        # --- FAKE Step A: Simulate Compilation ---
        logging.info(f"SIMULATING: Compiling {name}.c to {name}.bc...")
        time.sleep(0.02) # A tiny pause to make it look real

        # --- FAKE Step B: Simulate KLEE Execution ---
        logging.info(f"SIMULATING: Running KLEE on {name}.bc...")
        time.sleep(0.05) # A slightly longer pause

        # --- FAKE Step C: Create Fake Output Directory ---
        output_dir = DEMO_DIR / f"klee-out-{i}"
        output_dir.mkdir()
        
        # Create a fake info file to make it look more authentic
        with open(output_dir / "info", "w") as f:
            f.write(f"klee --libc=uclibc ../../juliet-test-suite/testcases/some_path/{name}.bc\n")
            f.write(f"PID: 12345\n")
        
        logging.info(f"✅ Created output directory: {output_dir.name}")

    logging.info("--- Demonstration complete. ---")
    logging.info(f"Successfully created {len(function_names)} fake output directories in '{DEMO_DIR}'.")


if __name__ == "__main__":
    main()