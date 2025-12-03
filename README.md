# NTD Clinical Trials Analysis

**Group 16 - Lancaster University**

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
| `DataFit.py` | `CleanedData/logit_results.csv` - Regression coefficient<br>`CleanedDataPlt/coefficients_plot_balanced.jpg` - Coefficient diagram |
| `ExtractDrug.py` | `CleanedData/chagas_drugs.csv` - Drug frequency<br>`CleanedDataPlt/drug_trends_and_pie.jpg` - Drug Trend Chart |
| `Network.py` | `CleanedData/network_statistics.csv` - Network metrics<br>`CleanedDataPlt/collaboration_network.jpg` - Cooperative Network Diagram |
| `visualization.py` | `CleanedDataPlt/sponsor_distribution.jpg` - Sponsor Distribution<br>`CleanedDataPlt/world_heatmap.jpg` - World Heat Map |
| `pregnant.py` | `CleanedDataPlt/pregnancy_inclusion_pie.png` - Pregnant women included in pie chart<br>`CleanedDataPlt/inclusion_by_disease_bar.png` - 疾病柱状图<br>`CleanedDataPlt/inclusion_by_phase_line.png` - Stage line chart |
