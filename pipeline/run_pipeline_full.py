import os
import subprocess
import datetime
import time
import sys

# Detect the correct Python executable (works for venv + cron)
PYTHON = sys.executable  # uses the active Python interpreter from the current environment

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def run_step(title, script):
    print(f"[{datetime.datetime.now()}] 🚀 Starting: {title}")
    start = time.time()
    try:
        # Always use the same Python interpreter that launched this script
        subprocess.run([PYTHON, script], check=True)
        print(f"[{datetime.datetime.now()}] ✅ Finished: {title} in {time.time()-start:.1f}s")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.datetime.now()}] ❌ Error in {title}: {e}")

if __name__ == "__main__":
    print("===============================================")
    print("🐷 FAST PRRSV FULL PIPELINE STARTED")
    print("===============================================")

    steps = [
        ("1️⃣ Fetching sequences from NCBI", "pipeline/01_fetch_ncbi_enhanced.py"),
        ("2️⃣ Running Quality Control", "pipeline/02_qc_and_metadata.py"),
        ("3️⃣ Aligning ORF5 Sequences", "pipeline/03_align_orf5.py"),
        ("4️⃣ Codon Alignment", "pipeline/04_codon_alignment.py"),
        ("5️⃣ Computing EII", "pipeline/05_compute_eii.py"),
    ]

    for title, script in steps:
        run_step(title, script)

    print(f"[{datetime.datetime.now()}] 🏁 PIPELINE RUN SUCCESSFULLY COMPLETED")

summary_file = f"logs/eii_summary_{datetime.datetime.now():%Y-%m-%d_%H-%M}.txt"
with open(summary_file, "w") as f:
    f.write(f"EII computation completed at {datetime.datetime.now()}\n")
    f.write("EII pipeline run completed successfully.\n")
print(f"📄 Summary saved to {summary_file}")

