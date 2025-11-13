import pandas as pd
import matplotlib.pyplot as plt
import os
from Maping import COUNTRY_CODE, HIGH_BURDEN_COUNTRIES
import geopandas as gpd

# 创建输出文件夹 Create output folder
os.makedirs("CleanedDataPlt", exist_ok=True)

# 读取数据 Read Data
df = pd.read_csv("CleanedData/cleaned_ictrp.csv", encoding="utf-8")
print(f"Total trials: {len(df)}")

# 筛选已发表的试验 Selected published 
published_df = df[df["results_posted"] == True]
print(f"Published: {len(published_df)}")
print(f"Unpublished: {len(df) - len(published_df)}\n")

# 统计赞助商类别  Statistics on sponsor categories
all_sponsor_counts = df["sponsor_category"].value_counts()
published_sponsor_counts = published_df["sponsor_category"].value_counts()

# 指定类别颜色 Specify category color
color_map = {
    'Industry': '#3498db',
    'Non-profit': '#e74c3c',
    'Government': '#2ecc71',
    'Other': '#95a5a6'
}

# 绘制对比图 Draw a comparison chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

for data, ax, title in [(all_sponsor_counts, ax1, 'All Trials'),
                        (published_sponsor_counts, ax2, 'Published Trials')]:

    # 根据类别获取对应颜色 Obtain corresponding colors based on categories
    colors = [color_map[cat] for cat in data.index]

    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=data.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10}
    )

    for autotext in autotexts:
        autotext.set_color('white')

    labels = [f'{cat}: {count}' for cat, count in zip(data.index, data.values)]
    ax.legend(labels, loc='upper left', fontsize=9)
    ax.set_title(title, fontsize=13, fontweight='bold')

fig.suptitle('Sponsor Category Distribution', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('CleanedDataPlt/sponsor_distribution.jpg', dpi=300, bbox_inches='tight')
plt.close()

industry_stats = pd.read_csv("CleanedData/country_Industry.csv", encoding="utf-8-sig")

# 添加负担分类列 Add burden classification column
industry_stats['burden_level'] = industry_stats['country'].apply(
    lambda x: 'High Burden' if x in HIGH_BURDEN_COUNTRIES else 'Normal'
)

# 保存更新后的文件 Save
industry_stats.to_csv("CleanedData/country_Industry_HighBurden.csv",
                      index=False, encoding="utf-8-sig")
burden_sum = industry_stats.groupby('burden_level')['count'].sum() # count burden level

# 画图 plt
fig, ax = plt.subplots(figsize=(10, 7))
ax.pie(burden_sum.values, labels=burden_sum.index, autopct='%1.1f%%',
       colors=['#e74c3c', '#3498db'], startangle=90)
ax.set_title('Industry Trials by Region', fontsize=14, fontweight='bold')
plt.savefig('CleanedDataPlt/industry_region.jpg', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Figure saved successfully!")

# 创建世界地图热力图 Create world map heatmap
country_stats = pd.read_csv("CleanedData/country_statistics.csv", encoding="utf-8-sig")

# 反转映射：国家名 -> ISO代码 Reverse mapping: country name -> ISO code
name_to_code = {v: k for k, v in COUNTRY_CODE.items()}
country_stats['iso_alpha'] = country_stats['country'].map(name_to_code)

# 读取地理数据 Read geographic data
world = gpd.read_file('countries.geo.json')

# 合并数据 Merge data
world = world.merge(country_stats, left_on='id', right_on='iso_alpha', how='left')

# 绘制地图 Plot map
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
world.plot(column='count', ax=ax, legend=True, cmap='YlOrRd',
           missing_kwds={'color': 'lightgrey', 'label': 'No data'},
           edgecolor='black', linewidth=0.5,
           legend_kwds={'label': 'Number of NTD Clinical Trials', 'shrink': 0.5})
ax.set_title('World Map: Number of NTD Clinical Trials by Country',
             fontsize=16, fontweight='bold', pad=20)
ax.axis('off')

# 保存JPG Save JPG
plt.savefig('CleanedDataPlt/world_heatmap.jpg', dpi=300, bbox_inches='tight')
plt.close()
print("✓ World heatmap saved as CleanedDataPlt/world_heatmap.jpg")

print("\n所有可视化完成！ All visualizations completed!")
