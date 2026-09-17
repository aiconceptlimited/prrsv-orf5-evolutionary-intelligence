# PRRSV ORF5 Evolutionary Intelligence Platform

**PRRSV ORF5 Evolutionary Intelligence Platform (EII)** is a computational research system for sequence-based analysis of evolutionary variation within the ORF5 region of porcine reproductive and respiratory syndrome virus (PRRSV).

The platform integrates sequence retrieval, quality control, ORF5 processing, multiple sequence alignment, codon-aware processing, sequence-derived evolutionary signal computation, site-level analysis, persistent result storage, and interactive research visualization.

**Live dashboard:** https://prrsv-orf5.aiconceptlimited.com.ng/  
**GitHub repository:** https://github.com/aiconceptlimited/prrsv-orf5-evolutionary-intelligence

---

## 1. Research Overview

PRRSV ORF5 is widely used in molecular characterization and comparative analysis of PRRSV because sequence variation within this region can provide information for investigating genetic diversity and evolutionary patterns.

This platform provides an integrated computational environment for examining ORF5 sequence variation and summarizing several sequence-derived characteristics within a common analytical framework.

The central output is the **Evolutionary Intelligence Index (EII)**, an implementation-specific composite index constructed from five computational signals:

1. Epitope Drift
2. Selection Pressure
3. Glycosylation Dynamics
4. Phylogenetic Instability
5. Distance Outliers

The platform is intended for **comparative sequence analysis, computational exploration, visualization, and hypothesis generation**. Its outputs require appropriate scientific interpretation and should not be treated as direct measurements of viral fitness, pathogenicity, transmission, vaccine escape, or clinical risk.

---

## 2. Research Objectives

The system is designed to support computational investigation of:

- ORF5 sequence diversity
- Conserved and variable alignment positions
- Sequence-derived evolutionary patterns
- Nucleotide and amino-acid variation
- Codon-level variability
- Glycosylation-related sequence motifs
- Pairwise sequence divergence
- Statistical distance outliers
- Site-level evolutionary summaries
- Integrated computational signal profiles

The framework is intended to allow multiple sequence-derived observations to be examined within a single research environment while retaining the individual components used to construct the composite index.

---

## 3. Key Capabilities

### Sequence and genomic processing

- PRRSV sequence retrieval from NCBI
- Sequence quality control
- Metadata processing
- ORF5 sequence extraction and processing
- Multiple sequence alignment
- Codon-aware alignment processing

### Evolutionary analysis

- Shannon entropy analysis
- Sequence-derived codon variability
- Glycosylation motif detection
- Pairwise sequence-distance analysis
- Statistical outlier analysis
- Site-level conservation analysis
- Selection-related site analysis

### Computational integration

- Multi-signal EII calculation
- Site-level composite scoring
- Persistent MySQL result storage
- Interactive Dash/Plotly visualization
- Modular Python pipeline
- Environment-based database configuration

---

## 4. Computational Workflow

The principal analytical workflow follows this sequence:

**Sequence retrieval → Quality control → ORF5 processing → Multiple sequence alignment → Codon-aware alignment → Evolutionary signal calculation → EII calculation → Site-level analysis → Database storage → Dashboard visualization**

The main orchestration script is:

```text
pipeline/run_pipeline_full.py
```

The principal EII calculation is implemented in:

```text
pipeline/05_compute_eii.py
```

---

## 5. Evolutionary Intelligence Index

The global EII is calculated from five sequence-derived signals.

For each signal, the current implementation first derives a raw value and normalizes the signal relative to the maximum raw value across the five components.

The composite index is then calculated as:

```text
EII = mean(normalized signal values) × 100
```

The resulting index is expressed on a **0–100 computational scale** under the current implementation.

### Interpretation

The EII should be understood as a **composite computational index defined by this software implementation**.

It is not a standardized evolutionary metric and does not independently establish:

- Viral fitness
- Virulence
- Transmission probability
- Vaccine escape
- Clinical severity
- Epidemiological risk
- A formal evolutionary rate
- A formal selection coefficient

The value is dependent on the input sequence cohort, alignment, signal definitions, normalization procedure, and implementation.

---

## 6. EII Signal Components

### 6.1 Epitope Drift

The Epitope Drift component uses **Shannon entropy** to quantify sequence variation across alignment positions.

For residue frequencies \(p_i\), Shannon entropy is calculated as:

```text
H = -Σ pᵢ log₂(pᵢ)
```

Higher entropy corresponds to greater sequence diversity at an alignment position.

Within the global EII workflow, entropy-derived values are aggregated and normalized before contributing to the composite index.

This is a sequence-variation measure. It should not be interpreted as experimentally demonstrated antigenic drift.

---

### 6.2 Selection Pressure

The canonical global EII implementation uses a **codon-variability measure**.

The workflow examines complete codons and quantifies the number of unique codon states observed across the analysed sequences.

This provides a sequence-derived representation of codon variability.

This component is **not equivalent to a dN/dS estimate** and should not be described as a formal positive- or negative-selection statistic.

The repository also contains separate site-level selection analyses. These should be interpreted independently from the global EII codon-variability component.

---

### 6.3 Glycosylation Dynamics

The glycosylation component identifies the canonical N-linked glycosylation sequence motif:

```text
N-X-S/T
```

where X represents any residue other than proline.

Detected motifs are converted into a sequence-derived signal for the EII calculation.

Motif detection alone does not establish:

- Glycan occupancy
- Glycosylation efficiency
- Structural exposure
- Biological function
- Immune consequences

Those conclusions require independent experimental or validated structural evidence.

---

### 6.4 Phylogenetic Instability

The current global EII implementation uses pairwise sequence differences among a sampled set of sequences.

Distances are calculated using comparable non-gap positions and summarized as a sequence-derived divergence signal.

This measure should not be interpreted as:

- A formal phylogenetic-instability statistic
- An evolutionary rate estimate
- A phylodynamic analysis
- A transmission reconstruction
- An effective population-size estimate

It is an implementation-specific sequence-distance signal.

---

### 6.5 Distance Outliers

The distance-outlier component identifies relatively distant observations using a statistical threshold based on:

```text
mean distance + 2 × standard deviation
```

This provides a computational method for identifying observations that are relatively distant within the analysed sequence set.

The threshold is statistical and implementation-specific. It is not a biological, clinical, or epidemiological risk threshold.

---

## 7. Site-Level Evolutionary Analysis

The platform also contains a site-level analytical framework for ORF5.

The site-level data include measures such as:

- Conservation
- Shannon entropy
- Sequence variability
- FEL-derived site information
- MEME-derived site information
- Selection-related scores
- Glycosylation-related frequency
- Composite site-level scores

The current site-level coordinate framework contains **209 ORF5 positions**.

Site-level scores are computational prioritization measures. A high-scoring site should be considered a candidate for further investigation rather than evidence of a confirmed biological mechanism.

---

## 8. Global EII and Site-Level Analysis Are Distinct

An important methodological distinction is maintained between the global EII and the site-level analysis.

### Global EII

The canonical global EII calculation uses the five signal definitions implemented directly in:

```text
pipeline/05_compute_eii.py
```

### Site-level analysis

The site-level framework incorporates additional information, including FEL and MEME-derived site results, conservation, entropy, variability, and glycosylation-related measures.

Therefore, **FEL and MEME should not be represented as direct components of the canonical five-signal global EII unless the implementation is explicitly changed to include them.**

This distinction is important when interpreting or reproducing results.

---

## 9. Data and Provenance

The platform is designed around PRRSV sequence records obtained from public sequence resources.

The public source repository intentionally separates software from production runtime data.

Large runtime datasets, database state, logs, temporary files, caches, backups, and deployment-specific material are not required to be committed to the public source repository.

For reproducible analysis, users should preserve:

- NCBI accession identifiers
- Sequence retrieval date
- Input sequence files
- Quality-control criteria
- Alignment settings
- Analysis parameters
- Software versions
- Generated outputs
- Database state or exported results
- Execution date

Because public sequence databases change over time, a future live retrieval can produce a different sequence cohort from an earlier run. Exact historical reproduction therefore requires preservation of the original accession set and input sequences.

---

## 10. Current Data Scope

The current ORF5 processing environment contains a cohort of **324 quality-controlled sequences** in the current alignment files.

The ORF5 site-level framework contains **209 analysed positions**.

These quantities describe the current computational materials and should not be interpreted as estimates of PRRSV prevalence, geographic prevalence, population size, or global viral diversity.

Different analytical outputs may originate from different processing dates or analytical stages. Results should therefore be interpreted according to their documented provenance rather than assuming that every stored output represents one synchronized pipeline execution.

---

## 11. Dashboard

The interactive research dashboard is implemented using:

- Dash
- Plotly
- Dash Bootstrap Components
- SQLAlchemy
- MySQL

The principal dashboard application is:

```text
dashboard_complete.py
```

The portable launcher is:

```text
start_dashboard.sh
```

Run:

```bash
./start_dashboard.sh
```

The live dashboard is:

**https://prrsv-orf5.aiconceptlimited.com.ng/**

The dashboard provides computational views of:

- Current EII
- Evolutionary signal composition
- Site-level evolutionary information
- Evolutionary patterns
- Hotspot-oriented site exploration
- Historical computational records where available

Dashboard values represent the state of the underlying computational database and may change when new analyses are performed.

---

## 12. Pipeline Components

The principal pipeline components are:

```text
pipeline/
├── 01_fetch_ncbi.py
├── 01_fetch_ncbi_enhanced.py
├── 02_qc_and_metadata.py
├── 03_align_orf5.py
├── 04_codon_alignment.py
├── 05_compute_eii.py
├── 06_export_publication_outputs.py
├── backtranslate_prank.py
├── export_qc_passed.py
├── remove_terminal_stop.py
├── run_pipeline_full.py
└── signals/
    ├── adaptive_selection.py
    ├── distance_outliers.py
    ├── epitope_drift.py
    ├── glycosylation_dynamics.py
    ├── phylogenetic_instability.py
    └── selection_pressure.py
```

The five signal modules provide supporting computational functionality. The canonical global EII implementation is defined by `05_compute_eii.py`.

---

## 13. Database Architecture

Persistent computational results are stored in MySQL.

Database configuration is provided through environment variables rather than hard-coded production credentials.

Example:

```env
DB_HOST=localhost
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=prrsv_genomics
```

The configuration template is:

```text
.env.example
```

The database schema is:

```text
database/schema.sql
```

Database utilities are provided in:

```text
database/utils.py
```

### Credential security

Production database credentials must never be committed to source control.

The public repository provides configuration templates only.

---

## 14. Installation

Clone the repository:

```bash
git clone https://github.com/aiconceptlimited/prrsv-orf5-evolutionary-intelligence.git
cd prrsv-orf5-evolutionary-intelligence
```

Create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Configure the database environment before running database-dependent components.

---

## 15. Running the Dashboard

After configuring the environment:

```bash
./start_dashboard.sh
```

The launcher uses the project's Python environment and starts:

```text
dashboard_complete.py
```

The launcher is written to use the project-relative installation path rather than a fixed deployment directory.

---

## 16. Running the Computational Pipeline

Activate the project environment:

```bash
source venv/bin/activate
```

Then run:

```bash
python pipeline/run_pipeline_full.py
```

The complete workflow coordinates:

1. Sequence retrieval
2. Quality control
3. ORF5 alignment
4. Codon-aware alignment
5. EII computation

Individual stages can also be executed independently when specific processing steps need to be inspected.

---

## 17. Reproducibility

The platform is intended to support reproducible computational research.

A reproducible analysis should preserve both software configuration and data provenance.

Recommended records include:

- Python version
- Dependency versions
- External executable versions
- NCBI accession identifiers
- Retrieval date
- Input sequence files
- Alignment parameters
- Signal definitions
- Normalization procedure
- Analysis parameters
- Output files
- Database state
- Execution date

The repository provides:

```text
requirements.txt
environment.yml
```

for environment specification.

Exact reproduction of a historical analysis cannot be guaranteed from software alone if the underlying public sequence database has subsequently changed.

---

## 18. Scientific Interpretation

The platform should be interpreted as a **computational framework for integrating sequence-derived observations**.

The scientific meaning of an output depends on:

- Input sequence composition
- Sequence quality
- Alignment quality
- Sampling
- Signal definition
- Normalization
- Coordinate framework
- Implementation version

Changes in any of these factors can alter the resulting computational values.

Accordingly, EII values from different analyses should be compared only when their methodological and input conditions are sufficiently comparable.

---

## 19. Scientific Limitations

### Composite-index limitation

EII is an implementation-specific composite index rather than a standardized evolutionary measurement.

### Sequence-derived limitation

Several signals are calculated directly from sequence characteristics and do not independently establish biological mechanisms.

### Selection limitation

The global selection component represents codon variability and is not a formal dN/dS analysis.

### Glycosylation limitation

N-X-S/T motif detection does not establish glycan occupancy or functional glycosylation.

### Distance limitation

Sequence distance does not independently establish transmission linkage or epidemiological connectivity.

### Site-score limitation

Site-level composite scores prioritize computational observations but do not establish biological importance.

### Temporal limitation

The current framework does not by itself constitute a formal temporal or phylodynamic analysis.

### Recombination limitation

The platform should not be interpreted as a comprehensive recombination-analysis framework unless a dedicated validated recombination workflow is explicitly added.

### Experimental-validation limitation

Computational outputs require independent experimental, structural, epidemiological, or literature-based evidence where biological conclusions are intended.

---

## 20. Research Applications

The platform can support research involving:

- PRRSV molecular evolution
- ORF5 sequence diversity
- Comparative genomic analysis
- Conservation analysis
- Variable-site exploration
- Sequence-derived evolutionary signals
- Candidate-site prioritization
- Computational surveillance research
- Research visualization
- Hypothesis generation
- Development of reproducible computational workflows

The framework is intended to complement formal evolutionary analysis, epidemiological investigation, structural analysis, and experimental research.

---

## 21. Repository Structure

```text
.
├── assets/
│   └── custom.css
├── database/
│   ├── schema.sql
│   └── utils.py
├── docs/
├── pipeline/
│   ├── sequence retrieval
│   ├── quality control
│   ├── alignment
│   ├── codon processing
│   ├── EII computation
│   └── signals/
├── scripts/
├── dashboard_complete.py
├── start_dashboard.sh
├── requirements.txt
├── environment.yml
├── .env.example
├── .gitignore
└── README.md
```

Runtime data, credentials, logs, caches, backups, and deployment-specific files are excluded from the public source release.

---

## 22. Software and Technologies

Core technologies include:

- Python
- Biopython
- NumPy
- Pandas
- SciPy
- Matplotlib
- MAFFT
- Dash
- Plotly
- Dash Bootstrap Components
- SQLAlchemy
- MySQL
- Requests
- tqdm

Exact Python package versions are specified in:

```text
requirements.txt
```

---

## 23. Development and Quality Principles

The platform follows several principles for computational research software.

### Scientific traceability

Computational outputs should remain traceable to their methods and input data.

### Explicit methodology

Implementation-specific measures should be described according to what the code actually calculates.

### Conservative interpretation

Computational predictions should not be presented as experimentally established biological effects without supporting evidence.

### Reproducibility

Software versions, configuration, input identifiers, and computational procedures should be preserved wherever possible.

### Data separation

Runtime data and production database state are separated from the public software source.

### Credential protection

Production credentials are excluded from source control.

### Versioned development

Changes to the computational framework should be tracked through source-control history.

---

## 24. Future Development

Potential future development includes:

- Formal codon-based selection analysis
- Temporal phylogenetic analysis
- Recombination analysis
- Expanded lineage and genotype annotation
- Improved accession-level provenance tracking
- Independent statistical evaluation of EII normalization
- Validation of individual signal components
- Integration of experimentally supported functional annotations
- Expanded workflow metadata
- More comprehensive reproducibility records

These are prospective development directions and are not represented as current capabilities unless implemented and validated.

---

## 25. Research Status

The platform is an active computational research system.

Software capabilities, analytical outputs, and scientific interpretations should be considered version-dependent.

Research conclusions derived from the platform should cite the specific software version, dataset, and analytical workflow used for the corresponding analysis.

---

## 26. Citation and Attribution

If this software or its methodology contributes to research, please cite the associated publication when available and acknowledge the software repository.

**PRRSV ORF5 Evolutionary Intelligence Platform**  
AI Concepts Limited  
Nigeria

Repository:

https://github.com/aiconceptlimited/prrsv-orf5-evolutionary-intelligence

---

## 27. Author

**Abubakar Garba, PhD**

AI Concepts Limited  
Nigeria

Research areas include:

- Computational veterinary virology
- Viral genomics
- Molecular evolution
- Computational immunology
- Immunoinformatics

---

## 28. License

No software license has currently been assigned to this repository.

Until a license is explicitly added, the source code should not be assumed to be released under an open-source license.

---

## 29. Disclaimer

This platform is provided for computational research and exploratory analysis.

Its outputs do not constitute:

- Clinical diagnoses
- Veterinary treatment recommendations
- Epidemiological forecasts
- Experimentally confirmed biological effects
- Measures of viral fitness
- Measures of pathogenicity
- Measures of transmission probability
- Vaccine-effectiveness estimates

Users should independently evaluate the underlying methods, input data, assumptions, and computational outputs before using results in research or downstream applications.
