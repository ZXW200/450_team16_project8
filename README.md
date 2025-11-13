# NTD Clinical Trials Analysis - Source Code Documentation

**Group 16** | Lancaster University | 2025

---

## 🚀 Quick Start

### Installation
```bash
pip install pandas numpy scikit-learn matplotlib networkx geopandas
```

### Execution (MUST run in this order)
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
dir CleanedDataPlt\*.png     # Should show 3 PNG files
dir CleanedDataPlt\*.jpg     # Should show 1 JPG file
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

## 1. CleanData.py - Data Cleaning & Preprocessing

**Purpose:** Transform raw WHO ICTRP data into analysis-ready format

**Input:** 
- `ictrp_data.csv` (315 raw trials)

**Key Functions:**

```python
classify_categories(sponsor_name) → str
    # Classifies sponsors into Government/Industry/Non-profit/Other
    # Uses keyword matching: PHARMA, UNIVERSITY, MINISTRY, etc.

map_income(code_str) → str
    # Maps ISO country codes to World Bank income levels
    # Returns: Low/Lower-middle/Upper-middle/High/Unknown

validate_age(age_text) → bool
    # Validates age ranges (0-120 years, 0-1440 months)
    # Returns True if biologically plausible

clean_html_tags(text) → str
    # Removes HTML formatting from text fields using regex
    # Pattern: r'<[^>]+>' → ''
```

**Processing Steps:**
1. Remove outliers (4 records: 2 sample size, 2 age anomalies)
2. Classify sponsors using keyword matching
3. Map countries to World Bank income classifications
4. Clean HTML tags from text fields
5. Impute missing values (median for numeric, "Unknown" for categorical)
6. Extract country statistics and create multiple output files

**Output Files (12 CSVs in CleanedData/):**
- `cleaned_ictrp.csv` - Main dataset (311 trials)
- `country_statistics.csv` - Trial counts by country (62 countries)
- `country_Industry.csv` - Industry-sponsored trials by country
- `published_trials.csv` - Trials with published results (13 trials)
- `pregnant_trials.csv` - Trials including pregnant women (12 trials)
- Plus 7 additional supporting CSV files

**Research Questions Addressed:** Foundation for all RQs (2.2.1-2.2.5)

---

## 2. DataFit.py - Logistic Regression Analysis

**Purpose:** Identify factors predicting trial results publication

**Input:**
- `CleanedData/cleaned_ictrp.csv`

**Method:**
- **Model:** Logistic Regression with OneHotEncoder pipeline
- **Features:** Phase, Study Type, Sponsor Category, Income Level
- **Target:** Results Posted (binary: published vs unpublished)
- **Split:** 80% train, 20% test (stratified, random_state=42)
- **Hyperparameters:** max_iter=2000

**Algorithm:**
```python
Pipeline([
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ("logit", LogisticRegression(max_iter=2000))
])
```

**Output:**
- `CleanedData/logit_results.csv` - Feature coefficients ranked by magnitude
- `CleanedDataPlt/coefficients_plot.png` - 4-panel visualization (Phase, Study Type, Sponsor, Income)

**Interpretation:**
- Positive coefficient = increases publication probability
- Negative coefficient = decreases publication probability
- Color-coded: Green (positive), Red (negative)

**Research Question Addressed:** RQ 2.2.1 (Publication factors)

---

## 3. ExtractDrug.py - Drug Trend Analysis

**Purpose:** Extract and analyze drug usage trends for Chagas disease

**Input:**
- `CleanedData/cleaned_ictrp.csv`

**Method:**
1. **Filter:** Select trials containing "Chagas" in condition or title (case-insensitive)
2. **Extract:** Use regex to extract drug names from intervention field
3. **Analyze:** Track top 5 drugs by year

**Extraction Pattern:**
```python
pattern = r'Drug:\s*([^;|\n]+)'
# Example: "Drug: Benznidazole; Device: Monitor" → "Benznidazole"
```

**Processing Steps:**
```python
# Step 1: Filter Chagas trials
chagas_df = df[df['condition'].str.contains('Chagas', case=False)]

# Step 2: Extract drug names
drugs = re.findall(r'Drug:\s*([^;|\n]+)', intervention_text)

# Step 3: Group by year and count
trend_data = drugs.groupby(['year', 'drug']).size()
```

**Output:**
- `CleanedData/chagas.csv` - All Chagas-related trials
- `CleanedData/chagas_drugs.csv` - Drug frequency counts
- `CleanedData/chagas_drug_trends.csv` - Top 5 drugs tracked over time

**Research Question Addressed:** RQ 2.2.5 (Drug trends for Chagas disease)

---

## 4. Network.py - Collaboration Network Analysis

**Purpose:** Reveal international partnership patterns between countries

**Input:**
- `CleanedData/cleaned_ictrp.csv`
- `CleanData.COUNTRY_CODE` (imported dictionary)

**Method:**
- **Graph Type:** Undirected, weighted network
- **Nodes:** Countries participating in trials
- **Edges:** Co-occurrence in multi-country trials
- **Weights:** Number of collaborative trials

**Algorithm:**
```python
G = nx.Graph()

# For each trial with multiple countries
for countries in multi_country_trials:
    for country_i, country_j in combinations(countries, 2):
        if G.has_edge(country_i, country_j):
            G[country_i][country_j]['weight'] += 1  # Increment
        else:
            G.add_edge(country_i, country_j, weight=1)  # Create
```

**Network Metrics Calculated:**

1. **Degree (Number of Partners)**
   - Counts unique collaboration partners
   - `degree(node) = |neighbors(node)|`

2. **Weighted Degree (Total Partnerships)**
   - Sums all collaboration instances
   - `weighted_degree(node) = Σ weight(edge)`

3. **Betweenness Centrality (Hub Score)**
   - Measures how often country lies on shortest paths
   - Range: [0, 1], higher = more central

**Output:**
- `CleanedData/network_statistics.csv` - Countries ranked by collaboration metrics

**Research Question Addressed:** RQ 2.2.2 (International partnerships)

---

## 5. visualization.py - Data Visualization

**Purpose:** Create publication-quality charts and geographic maps

**Input:**
- `CleanedData/cleaned_ictrp.csv`
- `CleanedData/country_Industry.csv`
- `CleanedData/country_statistics.csv`
- `countries.geo.json` (from [johan/world.geo.json](https://github.com/johan/world.geo.json))

**Generates 3 Visualizations:**

### Chart 1: Sponsor Distribution (Pie Charts)
```python
# Compares all trials vs published trials
fig, (ax1, ax2) = plt.subplots(1, 2)
# Color scheme: Industry=blue, Non-profit=red, Government=green, Other=black
```
- Shows percentage breakdown by sponsor category
- Highlights differences between all and published trials

### Chart 2: Industry Trials by Burden Level (Pie Chart)
```python
# Classifies countries as high burden or normal
high_burden = ['India', 'Mexico', 'Tanzania', 'Bangladesh', 'Bolivia',
               'Côte d\'Ivoire', 'Kenya', 'Egypt']
```
- Assesses whether pharmaceutical companies focus on disease hotspots
- Two categories: "High Burden" vs "Normal"

### Chart 3: World Heatmap (Choropleth Map)
```python
# Uses geopandas to create geographic visualization
world = gpd.read_file('countries.geo.json')
world = world.merge(country_stats, left_on='id', right_on='iso_alpha')
world.plot(column='count', cmap='YlOrRd', legend=True)
```

**Geographic Data Source:**
- File: `countries.geo.json`
- Source: https://github.com/johan/world.geo.json
- Format: GeoJSON with country boundaries and ISO codes
- License: Public domain

**Map Specifications:**
- Color scheme: Yellow → Orange → Red (increasing trial count)
- Missing data: Light grey
- Resolution: 300 DPI
- Format: JPG (smaller file size)

**Output:**
- `CleanedDataPlt/sponsor_distribution.png`
- `CleanedDataPlt/industry_region.png`
- `CleanedDataPlt/world_heatmap.jpg`

**Research Question Addressed:** RQ 2.2.3 (Pharmaceutical funding distribution)

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
