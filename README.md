# NTD Clinical Trials Analysis - Source Code Documentation

**Group 16** | Lancaster University | 2025

---

## 🚀 Quick Start

### Installation
```bash
pip install pandas numpy scikit-learn matplotlib networkx geopandas
```

### Execution (CleanData.py MUST RUN FIRST)
```bash
python CleanData.py          # Step 1: MUST run first
python DataFit.py            # Step 2
python ExtractDrug.py        # Step 3
python Network.py            # Step 4
python visualization.py      # Step 5
```

### Verify Outputs
```bash
dir CleanedData\*.csv        # Should show 12 CSV files
dir CleanedDataPlt\*.png     # Should show 4 PNG files

```

**Expected Runtime:** ~20-35 seconds for complete pipeline

---

## 📁 Source File Descriptions

This document explains the functionality of each source file in the project.

### Execution Order & Dependencies

```
1. CleanData.py          → Generates cleaned_ictrp.csv (required by all others)
2. DataFit.py            → Requires: cleaned_ictrp.csv
3. ExtractDrug.py        → Requires: cleaned_ictrp.csv
4. Network.py            → Requires: cleaned_ictrp.csv
5. visualization.py      → Requires: cleaned_ictrp.csv, country_*.csv, countries.geo.json
```
---

## 📊 Complete Output Files

### Datasets (CleanedData/ - 12 CSV files)
```
cleaned_ictrp.csv                    # Main dataset (311 trials)
country_statistics.csv               # Trial counts by country
country_Industry.csv                 # Industry trials by country
country_Industry_HighBurden.csv      # Industry trials with burden classification
published_trials.csv                 # Trials with published results
published_country_statistics.csv     # Published trials by country
pregnant_trials.csv                  # Trials including pregnant women
logit_results.csv                    # Regression coefficients
chagas.csv                           # Chagas disease trials
chagas_drugs.csv                     # Drug frequency counts
chagas_drug_trends.csv              # Top 5 drugs by year
network_statistics.csv              # Country collaboration metrics
```

### Visualizations (CleanedDataPlt/ - 4 image files)
```
coefficients_plot.png               # Logistic regression coefficients
sponsor_distribution.png            # Sponsor category comparison
industry_region.png                 # Industry trials by burden level
world_heatmap.jpg                   # Global trial distribution map
```

---

## 📚 Data Sources

- **Clinical Trials:** WHO International Clinical Trials Registry Platform (ICTRP)
- **Geographic Data:** johan/world.geo.json (https://github.com/johan/world.geo.json)
- **Income Classifications:** World Bank Country Classifications

---

## 👥 Team

**Group 16 - Lancaster University**
- Peizhe Jiang (Data Scientist)
- Congyao Ren (Data Analyst)
- Zixu Wang (Data Engineer)
- Alaghwani Balsam (Data Analyst)

**Project Host:** Infectious Diseases Data Observatory, University of Oxford

---

**Data Quality:** 311 valid trials (98.7% retention from 315 raw records)
