CREATE DATABASE IF NOT EXISTS prrsv_genomics;
USE prrsv_genomics;

CREATE TABLE IF NOT EXISTS sequences_raw (
    accession VARCHAR(30) PRIMARY KEY,
    sequence TEXT NOT NULL,
    collection_date DATE,
    location VARCHAR(100),
    host VARCHAR(50),
    subtype VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS qc_sequences (
    accession VARCHAR(30) PRIMARY KEY,
    sequence TEXT NOT NULL,
    quality_score FLOAT,
    passed_qc BOOLEAN,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eii_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    accession VARCHAR(30),
    signal_type VARCHAR(50),
    value FLOAT,
    time_window DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eii_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    time_window DATE,
    eii_value FLOAT,
    dominant_signal VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
