import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("CleanedDataPlt", exist_ok=True)

# print("开始读取数据...")
df = pd.read_csv("CleanedData/cleaned_ictrp.csv", encoding="utf-8")
print(f"Total: {len(df)} ")

published_df = df[df["results_posted"] == True].copy()
print(f"published: {len(published_df)} ")
print(f"unpublished: {len(df) - len(published_df)} ")

all_sponsor_counts = df["sponsor_category"].value_counts()
published_sponsor_counts = published_df["sponsor_category"].value_counts()

def parse_countries(countries_str):
    if pd.isna(countries_str):
        return []
    countries_str = str(countries_str)
    if ';' in countries_str:
        countries = countries_str.split(';')
    elif ',' in countries_str:
        countries = countries_str.split(',')
    else:
        countries = [countries_str]
    return [c.strip() for c in countries if c.strip() and c.strip() != 'Unknown']

# print("统计国家分布...")
country_counter = {}
for idx, row in published_df.iterrows():
    for country in parse_countries(row['countries']):
        country_counter[country] = country_counter.get(country, 0) + 1
published_countries_counts = pd.Series(country_counter).sort_values(ascending=False)

published_year_counts = published_df["Year"].value_counts().sort_index()

# print("\n开始生成图表...")

colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#95a5a6']

# 图1：全部试验赞助商分类
fig, ax = plt.subplots(figsize=(10, 7))
wedges, texts, autotexts = ax.pie(
    all_sponsor_counts.values,
    labels=all_sponsor_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'fontsize': 12, 'weight': 'bold'}
)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_weight('bold')
legend_labels = [f'{cat}: {count} trials' for cat, count in zip(all_sponsor_counts.index, all_sponsor_counts.values)]
ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
ax.set_title('All Trials - Sponsor Category Distribution', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('CleanedDataPlt/all_sponsor.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ all_sponsor.png saved")

# 图2：已发表试验赞助商分类
fig, ax = plt.subplots(figsize=(10, 7))
wedges, texts, autotexts = ax.pie(
    published_sponsor_counts.values,
    labels=published_sponsor_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'fontsize': 12, 'weight': 'bold'}
)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_weight('bold')
legend_labels = [f'{cat}: {count} trials' for cat, count in zip(published_sponsor_counts.index, published_sponsor_counts.values)]
ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
ax.set_title('Published Trials - Sponsor Category Distribution', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('CleanedDataPlt/published_sponsor.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ published_sponsor.png saved")

#Classfication high-risk country
#read data
industry_stats = pd.read_csv("CleanedData/country_Industry.csv", encoding="utf-8-sig")

# 定义高负担国家列表 Define high-burden countries
high_risk_countries = ['India', 'Mexico', 'Tanzania', 'Bangladesh', 'Bolivia',
                       'Côte d\'Ivoire', 'Kenya', 'Egypt']

# 添加负担分类列 Add burden level column
industry_stats['burden_level'] = industry_stats['country'].apply(
    lambda x: 'High Burden' if x in high_risk_countries else 'Normal'
)

# 保存更新后的文件 Save updated file
industry_stats.to_csv("CleanedData/country_Industry_HighBurden.csv",
                      index=False, encoding="utf-8-sig")
# draw table

#

print("\nAll Finished！")
