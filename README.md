# 🧬 PRRSV ORF5 Evolutionary Intelligence System (EII Platform)
## 🚀 Live System

- 🌐 Dashboard: https://prrsv-orf5.aiconceptlimited.com.ng/
- ⚙️ Automated pipeline: NCBI → QC → Alignment → EII
- 📊 Real-time evolutionary intelligence monitoring

## 📊 Live Dashboard

👉 https://prrsv-orf5.aiconceptlimited.com.ng/


## 🔍 Overview
This platform is designed for research, surveillance, and exploratory evolutionary analysis of PRRSV.
The **PRRSV ORF5 Evolutionary Intelligence System** is an automated genomic surveillance platform designed to monitor the evolutionary dynamics of PRRSV (Porcine Reproductive and Respiratory Syndrome Virus) using ORF5 gene sequences.

The system integrates multiple biologically meaningful signals into a unified metric called the **Evolutionary Intelligence Index (EII)**, enabling real-time tracking of viral evolution.

---

## 🚀 Key Features

* 🔄 Automated sequence retrieval from NCBI
* 🧪 Quality control and filtering of sequences
* 🧬 Multiple sequence alignment using MAFFT
* 🔗 Codon-aware sequence alignment
* 📊 Multi-signal evolutionary analysis:

  * Epitope Drift (Shannon entropy)
  * Selection Pressure (codon variability)
  * Glycosylation Dynamics (N-X-S/T motif detection)
  * Phylogenetic Instability (pairwise sequence divergence)
  * Distance Outliers (anomaly detection)
* 🗄️ MySQL database integration
* 📈 Real-time dashboard (Dash + Plotly)

---

## 🧠 Evolutionary Intelligence Index (EII)

The EII is computed as:

EII = mean(all normalized evolutionary signals) × 100

This produces a **single score (0–100)** representing the evolutionary activity of PRRSV.

---

## ⚙️ System Architecture

Pipeline workflow:

1. Fetch sequences from NCBI
2. Perform quality control
3. Align sequences (MAFFT)
4. Perform codon alignment
5. Compute evolutionary signals
6. Store results in database
7. Visualize via dashboard

---

## 📁 Project Structure

```
prrsv_eii/
│
├── pipeline/              # Core processing pipeline
├── dashboard/             # Visualization dashboard
├── data/                  # Generated data (ignored in Git)
├── logs/                  # Pipeline logs
├── docs/                  # Screenshots / assets
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

## 🔧 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/aiconceptlimited/prrsv-orf5-evolutionary-intelligence.git
cd prrsv-eii
```

---

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure database

Create a `.env` file:

```env
DB_HOST=localhost
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=prrsv_genomics
```

---

## ▶️ Running the System

### Run full pipeline

```bash
python pipeline/run_pipeline_full.py
```

---

### Launch dashboard

```bash
./start_dashboard.sh
```

Open in browser:

```
https://prrsv-orf5.aiconceptlimited.com.ng/

```

---

## 🔍 System Inspection (VERY IMPORTANT)

### Check raw sequences

```sql
SELECT COUNT(*) FROM sequences_raw;
SELECT accession, LENGTH(sequence) FROM sequences_raw LIMIT 5;
```

---

### Check QC results

```sql
SELECT COUNT(*) FROM qc_sequences;
SELECT * FROM qc_sequences LIMIT 5;
```

---

### Check EII history

```sql
SELECT * FROM eii_index ORDER BY created_at DESC LIMIT 10;
```

---

### Check evolutionary signals

```sql
SELECT * FROM eii_signals;
```

---

### Check latest snapshot

```sql
SELECT * FROM eii_latest;
```

---

### Inspect alignment files

```bash
head data/alignments/orf5_aligned.fasta
head data/alignments/orf5_codon_aligned.fasta
```

---

## 📊 Dashboard Features

* Real-time EII monitoring
* Signal composition visualization
* Evolutionary trend analysis
* Risk and impact classification

---

## 🧪 Scientific Notes

* **Epitope Drift** → Shannon entropy across alignment positions
* **Selection Pressure** → codon-level variation proxy
* **Glycosylation Dynamics** → N-X-S/T motif detection
* **Phylogenetic Instability** → mean pairwise Hamming distance
* **Distance Outliers** → extreme divergence detection

---

## 🤝 Contributions

Contributions are welcome:

* Improve biological accuracy (e.g., dN/dS models)
* Add phylogenetic tree inference
* Optimize performance
* Enhance dashboard features

---

## 📌 Future Improvements

* Integration with HyPhy / PAML for true selection analysis
* Phylogenetic tree visualization
* Geographic and temporal analysis
* API development
* Cloud deployment

---

## 👨‍💻 Author

Developed by **AI Concepts Limited, Nigeria**
For advanced virology research and genomic intelligence.

---

## ⚠️ Disclaimer

This system is intended for **research purposes only**.
Not for clinical or diagnostic use.

---

## 📜 License

MIT License

