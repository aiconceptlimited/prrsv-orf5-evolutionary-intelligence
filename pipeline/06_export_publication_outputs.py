"""
06_export_publication_outputs.py
--------------------------------
Generates publication-ready figures and tables from computed EII signals.
Outputs: PNG, PDF, and CSV in data/results/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from datetime import datetime

# --- Database config ---
config = {
    'host': 'localhost',
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'prrsv_genomics'
}

# --- Paths ---
base_dir = os.path.dirname(__file__)
signal_csv = os.path.join(base_dir, "../data/signals/eii_summary.csv")
results_dir = os.path.join(base_dir, "../data/results/")
os.makedirs(results_dir, exist_ok=True)

print("📊 Generating publication-ready outputs...")

# --- Load signal summary ---
df = pd.read_csv(signal_csv)
if df.empty:
    print("❌ No EII summary found. Run 05_compute_eii.py first.")
    exit(1)

# --- Retrieve from DB for consistency ---
import sqlalchemy

try:
    engine = sqlalchemy.create_engine(
        os.getenv("DATABASE_URL")
    )
    df_db = pd.read_sql("SELECT signal_name AS `Signal`, mean_value AS `NormalizedValue` FROM eii_signals", engine)
    df_index = pd.read_sql("SELECT eii_value, created_at FROM eii_index ORDER BY id DESC LIMIT 1", engine)
    print("✅ Retrieved latest EII values from database.")
except Exception as e:
    print(f"⚠️ Database read failed, using CSV only: {e}")
    df_db = df.copy()
    df_index = pd.DataFrame({'eii_value': [df['EII'].iloc[0]], 'created_at': [datetime.now()]})

    df_db = df.copy()
    df_index = pd.DataFrame({'eii_value': [df['EII'].iloc[0]], 'created_at': [datetime.now()]})

EII_value = df_index['eii_value'].iloc[0]
timestamp = df_index['created_at'].iloc[0]

# --- Plot 1: EII Signal Decomposition ---
plt.figure(figsize=(7, 5))
sns.barplot(x="Signal", y="NormalizedValue", data=df_db)
plt.title(f"Evolutionary Instability Index (EII) Signal Decomposition\nEII = {EII_value:.3f}", fontsize=12)
plt.ylabel("Normalized Value (0–1)")
plt.xticks(rotation=30)
plt.tight_layout()
bar_path = os.path.join(results_dir, "eii_signal_decomposition.png")
plt.savefig(bar_path, dpi=300)
plt.close()

# --- Plot 2: EII Contribution Pie ---
plt.figure(figsize=(6, 6))
plt.pie(df_db["NormalizedValue"], labels=df_db["Signal"], autopct="%1.1f%%", startangle=140)
plt.title("Relative Contribution of Each Signal", fontsize=12)
pie_path = os.path.join(results_dir, "eii_signal_contribution.png")
plt.savefig(pie_path, dpi=300)
plt.close()

# --- Plot 3: Heatmap (Signal Correlation) ---
plt.figure(figsize=(5, 4))
corr = df_db["NormalizedValue"].to_frame().T.corr()
sns.heatmap(corr.fillna(0), annot=True, cmap="Blues", square=True)
plt.title("Signal Correlation Matrix")
heat_path = os.path.join(results_dir, "eii_signal_correlation.png")
plt.savefig(heat_path, dpi=300)
plt.close()

# --- Export Combined Report ---
summary_path = os.path.join(results_dir, "eii_publication_summary.csv")
df_db["EII"] = EII_value
df_db["Timestamp"] = timestamp
df_db.to_csv(summary_path, index=False)

# --- Export PDF (optional text summary) ---
pdf_report = os.path.join(results_dir, "eii_summary_report.txt")
with open(pdf_report, "w") as f:
    f.write("Evolutionary Instability Index (EII) Summary Report\n")
    f.write(f"Generated: {timestamp}\n\n")
    f.write(f"Overall EII Value: {EII_value:.4f}\n\n")
    f.write("Signal Contributions:\n")
    for _, row in df_db.iterrows():
        f.write(f" - {row['Signal']}: {row['NormalizedValue']:.3f}\n")
    f.write("\nFigures saved to: data/results/\n")

print("✅ Publication outputs generated successfully:")
print(f"   - {bar_path}")
print(f"   - {pie_path}")
print(f"   - {heat_path}")
print(f"   - {summary_path}")
print(f"   - {pdf_report}")

