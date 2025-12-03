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
| `CleanData.py` | `CleanedData/cleaned_ictrp.csv` - 清洗后的数据集 |
| `DataFit.py` | `CleanedData/logit_results.csv` - 回归系数<br>`CleanedDataPlt/coefficients_plot_balanced.jpg` - 系数图 |
| `ExtractDrug.py` | `CleanedData/chagas_drugs.csv` - 药物频率<br>`CleanedDataPlt/drug_trends_and_pie.jpg` - 药物趋势图 |
| `Network.py` | `CleanedData/network_statistics.csv` - 网络指标<br>`CleanedDataPlt/collaboration_network.jpg` - 合作网络图 |
| `visualization.py` | `CleanedDataPlt/sponsor_distribution.jpg` - 赞助商分布<br>`CleanedDataPlt/world_heatmap.jpg` - 世界热力图 |
| `pregnant.py` | `CleanedDataPlt/pregnancy_inclusion_pie.png` - 孕妇纳入饼图<br>`CleanedDataPlt/inclusion_by_disease_bar.png` - 疾病柱状图<br>`CleanedDataPlt/inclusion_by_phase_line.png` - 阶段折线图 |
