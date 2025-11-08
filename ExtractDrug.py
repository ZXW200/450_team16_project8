import pandas as pd
import re

# The print statement is for test code and can be deleted at any time.
# print("正在读取数据...")
df = pd.read_csv('CleanedData/cleaned_ictrp.csv')
# print(f"总共 {len(df)} 条记录")

# 筛选出Chagas病相关的试验
#Screening for Chagas disease-related trials
chagas_df = df[
    df['standardised_condition'].str.contains('Chagas', case=False, na=False) |
    df['original_condition'].str.contains('Chagas', case=False, na=False) |
    df['study_title'].str.contains('Chagas', case=False, na=False)
].copy()

# print(f"\n找到 {len(chagas_df)} 条Chagas病相关试验")

# 保存基本信息
#Save basic information
chagas_df.to_csv("CleanedData/chagas.csv", index=False, encoding='utf-8-sig')
# print("已保存基本数据")
# # ========== Extracting drug =========
# # ========== 提取药物信息 ==========
# print("\n开始提取药物信息...")

# 处理日期
# Processing date
chagas_df['date_registration'] = pd.to_datetime(chagas_df['date_registration'], errors='coerce')
chagas_df['year'] = chagas_df['date_registration'].dt.year

# 移除没有日期的记录
# remove missingdata 
chagas_df = chagas_df.dropna(subset=['year']).copy()
# print(f"有有效日期的试验: {len(chagas_df)} 条")

# 提取所有药物和对应的年份
# Extract all drugs and their corresponding years.
drug_year_list = []

for idx, row in chagas_df.iterrows():
    text = row['intervention']
    year = row['year']
    
    if pd.isna(text):
        continue
    
    # 提取 'Drug:' 后面的内容
    # Extract the content after 'Drug:'
    drugs = re.findall(r'Drug:\s*([^;|\n]+)', str(text), flags=re.IGNORECASE)
    
    for drug in drugs:
        drug_clean = drug.strip()
        drug_year_list.append({'drug': drug_clean, 'year': int(year)})

# 转换为DataFrame 
# turn to DataFrame
drug_year_df = pd.DataFrame(drug_year_list)
# print(f"提取到 {len(drug_year_df)} 条药物记录")
#Statistics on the most common drugs
#统计最常见的药物
drug_counts = drug_year_df['drug'].value_counts()
# print("\nhead10:")
# print(drug_counts.head(10))

# 保存 Save
drug_counts.to_csv("CleanedData/chagas_drugs.csv", header=['Count'], encoding='utf-8-sig')

#Statistical Trends by Year 
#按年份统计趋势
# 选择前5种最常见的药物
# select top 5 drug
top_5_drugs = drug_counts.head(5).index.tolist()
# print(f"\n分析前5种药物的趋势: {top_5_drugs}")

# 筛选这5种药物的数据
# Data from screening these 5 drugs
drug_year_top5 = drug_year_df[drug_year_df['drug'].isin(top_5_drugs)]

# 按年份和药物分组统计
# Statistics by year and drug grouping
trend_data = drug_year_top5.groupby(['year', 'drug']).size().reset_index(name='count')

# 保存趋势数据
trend_data.to_csv("CleanedData/chagas_drug_trends.csv", index=False, encoding='utf-8-sig')
print("saved")


