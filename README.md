# NTD Clinical Trials Analysis

**Group 16 - Lancaster University**

## Data Sources

| File | Source |
|------|--------|
| `ictrp_data.csv` | Infectious Diseases Data Observatory (IDDO), University of Oxford |
| `countries.geo.json` | [geo-countries](https://github.com/datasets/geo-countries) - GitHub |

## Requirements

```bash
pip install pandas numpy scikit-learn matplotlib networkx geopandas
```

## Usage

```bash
python Main.py
```

## Scripts & Outputs

| Script | Output |
|--------|--------|
| `CleanData.py` | `CleanedData/cleaned_ictrp.csv` - Cleaned dataset |
| `DataFit.py` | `CleanedData/logit_results.csv` - Regression coefficients<br>`CleanedDataPlt/coefficients_plot_balanced.jpg` - Coefficient plot |
| `ExtractDrug.py` | `CleanedData/chagas_drugs.csv` - Drug frequency<br>`CleanedDataPlt/drug_trends_and_pie.jpg` - Drug trend chart |
| `Network.py` | `CleanedData/network_statistics.csv` - Network metrics<br>`CleanedDataPlt/collaboration_network.jpg` - Collaboration network |
| `visualization.py` | `CleanedDataPlt/sponsor_distribution.jpg` - Sponsor distribution<br>`CleanedDataPlt/world_heatmap.jpg` - World heatmap |
| `pregnant.py` | `CleanedDataPlt/pregnancy_inclusion_pie.png` - Inclusion pie chart<br>`CleanedDataPlt/inclusion_by_disease_bar.png` - Disease bar chart<br>`CleanedDataPlt/inclusion_by_phase_line.png` - Phase line chart |
