# NTD Clinical Trials Analysis - Code Submission

**Group 16** | Lancaster University | 2025

## Quick Start

### Installation
```bash
pip install pandas numpy scikit-learn matplotlib networkx
```

### Execution Order (IMPORTANT!)
```bash
python CleanData.py          # Step 1: Data cleaning (MUST run first)
python DataFit.py            # Step 2: Logistic regression
python ExtractDrug.py        # Step 3: Drug analysis
python Network.py            # Step 4: Network analysis
python visualization.py      # Step 5: Visualizations
```

## File Overview

| File | Purpose | Research Question |
|------|---------|-------------------|
| `CleanData.py` | Data cleaning & preprocessing | Foundation for all RQs |
| `DataFit.py` | Logistic regression analysis | RQ 2.2.1 (Publication factors) |
| `ExtractDrug.py` | Chagas drug trend analysis | RQ 2.2.5 (Drug trends) |
| `Network.py` | Country collaboration network | RQ 2.2.2 (Partnerships) |
| `visualization.py` | Sponsor & regional charts | RQ 2.2.3 (Pharma funding) |

## Outputs

### Datasets (12 CSV files in `CleanedData/`)
- `cleaned_ictrp.csv` - Main cleaned dataset (311 trials)
- `logit_results.csv` - Regression coefficients
- `network_statistics.csv` - Country collaboration metrics
- `chagas_drug_trends.csv` - Top 5 drugs by year
- *...and 8 more supporting files*

### Visualizations (3 PNG files in `CleanedDataPlt/`)
- `coefficients_plot.png` - Regression coefficients
- `sponsor_distribution.png` - Sponsor category comparison
- `industry_region.png` - Industry trials by burden level

## Key Statistics

- **Data**: 311 trials (1999-2023) across 62 countries
- **Publication rate**: 4.2% (13/311)
- **Sponsors**: Non-profit 66.9% | Other 21.2% | Industry 7.4% | Government 4.5%

## Full Documentation

See `CODE_DOCUMENTATION.txt` for detailed technical documentation.
