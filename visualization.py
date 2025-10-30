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

# 图3：已发表国家TOP20
top_countries = published_countries_counts.head(20)
fig, ax = plt.subplots(figsize=(12, 10))
ax.barh(range(len(top_countries)), top_countries.values, color='#3498db')
ax.set_yticks(range(len(top_countries)))
ax.set_yticklabels(top_countries.index, fontsize=11)
for i, (country, count) in enumerate(zip(top_countries.index, top_countries.values)):
    pct = count / len(published_df) * 100
    ax.text(count + 3, i, f'{int(count)} ({pct:.1f}%)', va='center', fontsize=9, fontweight='bold')
ax.set_xlabel('Number of Published Trials', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Trial Countries in Published Trials', fontsize=16, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('CleanedDataPlt/published_country.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ published_country.png saved")

# 图4：年度趋势
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(published_year_counts.index, published_year_counts.values, marker='o', linewidth=2, markersize=6, color='#3498db')
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Published Trials', fontsize=12, fontweight='bold')
ax.set_title('Published Trials by Year (1993-2023)', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xticks(range(int(published_year_counts.index.min()), int(published_year_counts.index.max()) + 1, 2))
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('CleanedDataPlt/published_yearly.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ published_yearly.png saved")

print("\n所有图表生成完成！")
