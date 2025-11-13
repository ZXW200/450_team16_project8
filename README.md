# NTD Clinical Trials Analysis - Code Submission

**Group 16** | Lancaster University | 2025

---

## 📋 Project Overview

This project analyzes trends in Neglected Tropical Disease (NTD) clinical trials using data from WHO's International Clinical Trials Registry Platform (ICTRP), covering 315 trials from 1999-2023 across 62 countries.

**Key Research Questions:**
- RQ 2.2.1: What factors are associated with results publication?
- RQ 2.2.2: Can network analysis reveal partnerships and hub countries?
- RQ 2.2.3: What proportion of trials are funded by pharmaceutical companies, and do they align with high-burden regions?
- RQ 2.2.4: Are vulnerable populations (children, pregnant women) included in studies?
- RQ 2.2.5: For Chagas disease, which drugs are studied and how have trends evolved?

---

## 🚀 Quick Start

### Prerequisites

**Required Python Version:** Python 3.7+

**Required Dependencies:**
```bash
pip install pandas numpy scikit-learn matplotlib networkx geopandas
```

**Alternative Installation (if above fails):**
```bash
# For conda users (recommended for geopandas)
conda install pandas numpy scikit-learn matplotlib networkx geopandas

# Or install individually
pip install pandas numpy scikit-learn matplotlib networkx
pip install geopandas  # May require additional system dependencies
```

---

## 📂 Project Structure

```
450_team16_project8-main/
├── ictrp_data.csv                      # Input: Raw WHO ICTRP data
├── countries.geo.json                  # Geographic data for world map
├── CleanData.py                        # Script 1: Data cleaning
├── DataFit.py                          # Script 2: Logistic regression
├── ExtractDrug.py                      # Script 3: Drug extraction
├── Network.py                          # Script 4: Network analysis
├── visualization.py                    # Script 5: Visualizations
├── CODE_DOCUMENTATION.txt              # Detailed technical documentation
├── README.md                           # This file
├── CleanedData/                        # Output: Cleaned datasets (12 CSV files)
└── CleanedDataPlt/                     # Output: Visualizations (PNG files)
```

---

## ⚙️ Execution Order (CRITICAL!)

**Scripts must be run in the following order:**

```bash
# Step 1: Data Cleaning (MUST run first)
python CleanData.py

# Step 2: Logistic Regression Analysis
python DataFit.py

# Step 3: Drug Extraction & Trend Analysis
python ExtractDrug.py

# Step 4: Network Analysis
python Network.py

# Step 5: Visualizations (includes world map)
python visualization.py
```

**Why this order matters:**
- `CleanData.py` generates `cleaned_ictrp.csv` which is required by all other scripts
- Each subsequent script depends on outputs from previous steps
- Running out of order will result in `FileNotFoundError`

---

## 📊 File Descriptions

### Analysis Scripts

| File | Purpose | Research Question | Key Outputs |
|------|---------|-------------------|-------------|
| **CleanData.py** | Data cleaning & preprocessing | Foundation for all RQs | `cleaned_ictrp.csv`, country statistics |
| **DataFit.py** | Logistic regression analysis | RQ 2.2.1 (Publication factors) | `logit_results.csv`, coefficients plot |
| **ExtractDrug.py** | Chagas drug trend analysis | RQ 2.2.5 (Drug trends) | `chagas_drugs.csv`, drug trends |
| **Network.py** | Country collaboration network | RQ 2.2.2 (Partnerships) | `network_statistics.csv` |
| **visualization.py** | Sponsor & regional visualizations | RQ 2.2.3 (Pharma funding) | Sponsor charts, world heatmap |

### Data Files

**Input Files:**
- `ictrp_data.csv` - Raw clinical trial data from WHO ICTRP (315 trials)
- `countries.geo.json` - Geographic boundaries for world map visualization
  - **Source:** [johan/world.geo.json](https://github.com/johan/world.geo.json)
  - **Description:** Annotated GeoJSON geometry files for the world
  - **License:** Public domain
  - **Usage:** Used in `visualization.py` to create the world heatmap

**Output Files (Generated):**

*In `CleanedData/` folder (12 CSV files):*
- `cleaned_ictrp.csv` - Main cleaned dataset (311 trials after outlier removal)
- `country_statistics.csv` - Trial counts by country
- `country_Industry.csv` - Industry-sponsored trials by country
- `country_Industry_HighBurden.csv` - Industry trials classified by burden level
- `published_trials.csv` - Trials with published results (13 trials)
- `published_country_statistics.csv` - Published trials by country
- `pregnant_trials.csv` - Trials including pregnant women (12 trials)
- `logit_results.csv` - Logistic regression coefficients
- `chagas.csv` - All Chagas disease-related trials
- `chagas_drugs.csv` - Drug frequency counts
- `chagas_drug_trends.csv` - Top 5 drugs by year
- `network_statistics.csv` - Country collaboration metrics

*In `CleanedDataPlt/` folder (4 visualization files):*
- `coefficients_plot.png` - Logistic regression coefficients by category
- `sponsor_distribution.png` - Sponsor category comparison (all vs published)
- `industry_region.png` - Industry trials by burden level (pie chart)
- `world_heatmap.jpg` - World map showing trial distribution by country

---

## 📈 Key Statistics

**Data Summary:**
- **Total Trials:** 311 (after cleaning from original 315)
- **Time Range:** 1999-2023
- **Countries Involved:** 62
- **Publication Rate:** 4.2% (13/311 trials)

**Sponsor Distribution:**
- Non-profit: 66.9% (208 trials)
- Other: 21.2% (66 trials)
- Industry: 7.4% (23 trials)
- Government: 4.5% (14 trials)

**Data Quality:**
- Outliers Removed: 4 records (1.3%)
  - 2 sample size anomalies (negative or >1 million)
  - 2 age range anomalies (>120 years)

---

## 🗺️ Geographic Data Attribution

### World Map (countries.geo.json)

**Source Repository:** [johan/world.geo.json](https://github.com/johan/world.geo.json)

**Description:**
- Annotated GeoJSON geometry files containing world country boundaries
- Includes country names, ISO codes, and geographic coordinates
- Used for creating choropleth maps in `visualization.py`

**Citation:**
```
Geographic data source: johan/world.geo.json
Available at: https://github.com/johan/world.geo.json
```

**Usage in This Project:**
```python
# In visualization.py
world = gpd.read_file('countries.geo.json')
world = world.merge(country_stats, left_on='id', right_on='iso_alpha', how='left')
world.plot(column='count', cmap='YlOrRd', legend=True)
```

**Alternative Option:**
If `countries.geo.json` is not available, you can use Natural Earth data:
```python
# Download from: https://www.naturalearthdata.com/
world = gpd.read_file('ne_110m_admin_0_countries.shp')
world = world.merge(country_stats, left_on='ISO_A3', right_on='iso_alpha', how='left')
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. `FileNotFoundError: ictrp_data.csv`
**Solution:** Ensure the raw data file is in the same directory as the scripts.

#### 2. `AttributeError: module 'gpd' has no attribute 'read_file'`
**Cause:** Naming conflict - you may have a file named `gpd.py` or `geopandas.py` in your project folder.

**Solution:**
```bash
# Check for conflicting files
dir *.py | findstr /i "gpd geopandas pandas"

# Rename any conflicting files
ren gpd.py gpd_backup.py
ren geopandas.py geopandas_backup.py

# Clear Python cache
rmdir /s /q __pycache__

# Re-run the script
python visualization.py
```

#### 3. `FileNotFoundError: countries.geo.json`
**Solution Option A:** Download the GeoJSON file:
```bash
# From GitHub
curl -O https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json
```

**Solution Option B:** Modify `visualization.py` to use Natural Earth shapefile:
```python
# Replace line: world = gpd.read_file('countries.geo.json')
# With:
try:
    world = gpd.read_file('countries.geo.json')
    id_field = 'id'
except FileNotFoundError:
    print("Using Natural Earth shapefile as fallback...")
    world = gpd.read_file('ne_110m_admin_0_countries.shp')
    id_field = 'ISO_A3'

# Update merge line accordingly
world = world.merge(country_stats, left_on=id_field, right_on='iso_alpha', how='left')
```

#### 4. `ImportError: No module named 'geopandas'`
**Solution:**
```bash
# Try conda (recommended)
conda install geopandas

# Or pip with system packages
pip install geopandas --break-system-packages

# On Windows, you may need to install dependencies first
pip install fiona pyproj shapely
pip install geopandas
```

#### 5. Missing Data Issues
**If you see unexpected NaN values or empty outputs:**
- Verify `CleanData.py` ran successfully
- Check that `CleanedData/` folder was created with 12 CSV files
- Re-run `CleanData.py` if any files are missing

---

## 📊 Research Questions & Methods

### RQ 2.2.1: Publication Factors (DataFit.py)
**Method:** Logistic regression with one-hot encoding
**Features:** Phase, Study Type, Sponsor Category, Income Level
**Target:** Results Posted (binary)
**Output:** Coefficient plot showing positive/negative predictors

### RQ 2.2.2: International Partnerships (Network.py)
**Method:** Network graph analysis using NetworkX
**Metrics:** Degree centrality, weighted degree, betweenness centrality
**Output:** `network_statistics.csv` ranking countries by collaboration

### RQ 2.2.3: Pharmaceutical Funding (visualization.py)
**Method:** Comparative analysis with geographic visualization
**Analysis:** Industry trials vs high-burden countries
**Output:** Pie charts and world heatmap

### RQ 2.2.4: Vulnerable Populations (CleanData.py)
**Method:** Field extraction and filtering
**Focus:** Pregnant women (children data insufficient)
**Output:** `pregnant_trials.csv` (12 trials identified)

### RQ 2.2.5: Chagas Drug Trends (ExtractDrug.py)
**Method:** Regex pattern matching and temporal analysis
**Extraction:** Drug names from intervention field
**Output:** Top 5 drugs tracked over time

---

## 📚 Data Processing Pipeline

### 1. Data Cleaning (CleanData.py)
**Input:** Raw ICTRP data (315 trials)
**Operations:**
- Remove HTML tags from text fields
- Validate sample sizes (0 < size ≤ 1,000,000)
- Validate age ranges (0-120 years)
- Classify sponsors (Government/Industry/Non-profit/Other)
- Map countries to World Bank income levels
- Handle missing values (median for numeric, "Unknown" for categorical)

**Output:** 311 valid trials (4 outliers removed)

### 2. Statistical Analysis (DataFit.py)
**Method:** Scikit-learn Pipeline with OneHotEncoder and Logistic Regression
**Train/Test Split:** 80/20, stratified by target variable
**Regularization:** Max iterations = 2000

### 3. Text Mining (ExtractDrug.py)
**Pattern:** `Drug:\s*([^;|\n]+)`
**Languages:** Case-insensitive matching
**Temporal:** Grouped by registration year

### 4. Network Construction (Network.py)
**Graph Type:** Undirected, weighted
**Nodes:** Countries (from trial participation)
**Edges:** Co-occurrence in multi-country trials
**Weights:** Number of collaborative trials

### 5. Visualization (visualization.py)
**Charts:**
- Pie charts: Sponsor distribution comparison
- Choropleth map: Geographic trial distribution
**Libraries:** Matplotlib, GeoPandas

---

## 🎓 Academic Use

### Citation
If using this code or methodology, please cite:
```
Group 16 (2025). Investigating Trends in Neglected Tropical Disease Clinical Studies.
Lancaster University. Data source: WHO ICTRP (1999-2023).
```

### Data Sources
- **Clinical Trials:** WHO International Clinical Trials Registry Platform (ICTRP)
- **Geographic Data:** johan/world.geo.json (https://github.com/johan/world.geo.json)
- **Income Classification:** World Bank Country Classifications

---

## 👥 Team

**Group 16 - Lancaster University**
- Peizhe Jiang (Data Scientist)
- Congyao Ren (Data Analyst)
- Zixu Wang (Data Engineer)
- Alaghwani Balsam (Data Analyst)

**Project Host:** Infectious Diseases Data Observatory, University of Oxford  
**Contact:** Rhys Peploe (Statistician)

---

## 📄 License & Usage

- Code: Available for academic and educational purposes
- Data: Subject to WHO ICTRP terms of use
- Geographic data: Public domain (johan/world.geo.json)

---

## 📞 Support

**For Detailed Documentation:**
- See `CODE_DOCUMENTATION.txt` for comprehensive technical details
- See `CODE_DOCUMENTATION.txt` for complete method descriptions

**For Issues:**
1. Check that all dependencies are installed
2. Verify execution order
3. Ensure `countries.geo.json` is present
4. Check Python version (3.7+ required)

---

## 🔄 Version History

- **Version 1.13.3** (13.11.2025): Current release
  - Data cleaning with outlier detection
  - Network analysis implementation
  - Geographic visualization with world heatmap

---

## ✅ Checklist Before Running

- [ ] Python 3.7+ installed
- [ ] All dependencies installed (`pandas`, `numpy`, `scikit-learn`, `matplotlib`, `networkx`, `geopandas`)
- [ ] `ictrp_data.csv` present in project directory
- [ ] `countries.geo.json` present in project directory (or Natural Earth shapefile as backup)
- [ ] No naming conflicts (no files named `gpd.py`, `geopandas.py`, `pandas.py`, etc.)
- [ ] Sufficient disk space for output files (~50 MB)

---

## 🎯 Expected Runtime

- `CleanData.py`: ~5-10 seconds
- `DataFit.py`: ~2-5 seconds
- `ExtractDrug.py`: ~1-2 seconds
- `Network.py`: ~2-3 seconds
- `visualization.py`: ~10-15 seconds (map rendering)

**Total:** ~20-35 seconds for complete pipeline

---

**Last Updated:** November 13, 2025  
**Repository:** 450_team16_project8-main
