#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取Chagas病(查加斯病)相关的临床试验信息
"""

import pandas as pd
import re


print("正在读取数据...")
df = pd.read_csv('CleanedData/cleaned_ictrp.csv')

print(f"总共 {len(df)} 条记录")

    # 筛选出Chagas病相关的试验
chagas_df = df[
        df['standardised_condition'].str.contains('Chagas', case=False, na=False) |
        df['original_condition'].str.contains('Chagas', case=False, na=False) |
        df['study_title'].str.contains('Chagas', case=False, na=False)
].copy()

print(f"\n找到 {len(chagas_df)} 条Chagas病相关试验")

    # 提取关键信息
result_data = []

for idx, row in chagas_df.iterrows():
    record = {
        'trial_id': row.get('trial_id', ''),
        'study_title': row.get('study_title', ''),
        'standardised_condition': row.get('standardised_condition', ''),
        'original_condition': row.get('original_condition', ''),
        'intervention': row.get('intervention', ''),
        'countries': row.get('countries', ''),
        'date_registration': row.get('date_registration', ''),
        'date_enrollment': row.get('date_enrollment', ''),
        'phase': row.get('phase', ''),
        'study_type': row.get('study_type', ''),
        'target_sample_size': row.get('target_sample_size', ''),
        'primary_sponsor': row.get('primary_sponsor', ''),
        'results_ind': row.get('results_ind', ''),
    }
    result_data.append(record)

    # 创建结果数据框
result_df = pd.DataFrame(result_data)

    # 保存为CSV
result_df.to_csv("CleanedData/changas.csv", index=False, encoding='utf-8-sig')
print(f"\n已保存为CSV: ")

    # 保存为Excel

# 从 chagas_df 的 intervention 列提取药物信息 (使用 re.findall)
drug_list = []
for text in chagas_df['intervention']:
    if pd.isna(text):
        continue
    # 提取 'Drug:' 后面的内容 (不区分大小写)
    drugs = re.findall(r'Drug:\s*([^;|\n]+)', str(text), flags=re.IGNORECASE)
    drug_list.extend(drugs)

# 3. 清理和去重
# 接着你的代码：

# 3. 清理和去重
drug_list = [drug.strip() for drug in drug_list]
unique_drugs = list(set(drug_list))

# 4. 用pandas统计药物频次
drug_series = pd.Series(drug_list)
drug_counts = drug_series.value_counts()

# 5. 转换为DataFrame
drug_df = drug_counts.reset_index()
drug_df.columns = ['Drug', 'Count']

print(f"\n共发现 {len(unique_drugs)} 种不同的药物")
print("\n最常用的药物:")
print(drug_df.head(10))

# 6. 保存
drug_df.to_csv("CleanedData/chagas_drugs.csv", index=False, encoding='utf-8-sig')
print("\n药物统计已保存")

