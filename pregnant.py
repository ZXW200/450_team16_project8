import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

plt.style.use('default')
sns.set_palette('husl')

Input = 'CleanedData/cleaned_ictrp.csv'
Output = 'CleanedData/wofageinidenage.csv'

print("Loading data...")
df = pd.read_csv(Input)
print("Data loaded. Shape:", df.shape)

def Inclusion(row):
    """
    排除EXCLUDED_出现exclude/no pregnant/not allowed等关键字
    包含INCLUDED_出现allow/include/eligible/pregnant等关键字
    提及无法明确MENTIONED_UNCLEAR
    没提到pregnant标注为UNKNOWN
    """

    # 合并相关字段文本
    txt = ' '.join([
        str(row.get('inclusion_criteria', '')),
        str(row.get('exclusion_criteria', '')),
        str(row.get('pregnant_participants', ''))
    ]).lower()

    # 未提及怀孕相关关键词
    if not any(x in txt for x in ['pregnan', 'pregnancy', 'pregnant']):
        return 'UNKNOWN'

    #排除标志
    exclude_patterns = [
        r'no pregnant', r'no pregnancy', r'exclud', r'not allow', r'prohibit'
    ]
    if any(re.search(p, txt) for p in exclude_patterns):
        return 'EXCLUDED'

    #纳入标志
    include_patterns = [
        r'allow', r'include', r'eligible', r'permit', r'accept'
    ]
    if any(re.search(p, txt) for p in include_patterns):
        return 'INCLUDED'

    #提到但是不清楚
    return 'MENTIONED_UNCLEAR'


print("\nRunning improved pregnancy detection...")
df['pregnant_included'] = df.apply(Inclusion, axis=1)
print(df['pregnant_included'].value_counts())


def clean_phase(p):
    if pd.isna(p): 
        return 'Unknown'
    s = str(p).lower()

    mapping = {
        'phase iv': 'Phase IV',
        'phase 4': 'Phase IV',
        'phase iii': 'Phase III',
        'phase 3': 'Phase III',
        'phase ii': 'Phase II',
        'phase 2': 'Phase II',
        'phase i': 'Phase I',
        'phase 1': 'Phase I'
    }

    for i, val in mapping.items():
        if i in s:
            return val

    if 'not applicable' in s:
        return 'Not Applicable'

    return 'Unknown'


df['phase_category'] = df['phase'].apply(clean_phase) if 'phase' in df.columns else 'Unknown'


def Disease(cond):
    if pd.isna(cond):
        return 'Unknown'

    s = cond.lower()

    rules = [
        (['malaria'], 'Malaria'),
        (['schisto', 'helminth', 'worm', 'parasite'], 'Parasitic Diseases'),
        (['hiv', 'virus', 'covid', 'ebola'], 'Viral Diseases'),
        (['tb', 'tuberculosis'], 'Bacterial Diseases'),
        (['diabetes'], 'Metabolic Disorders'),
        (['cancer', 'tumor'], 'Oncology'),
        (['maternal', 'pregnan'], 'Maternal/Reproductive'),
    ]

    for j, label in rules:
        if any(k in s for k in j):
            return label

    return 'Other'


df['disease_category'] = df['standardised_condition'].apply(Disease)


#计算统计数据
print("\nComputing statistics:")

# 过滤掉不明确的UNKNOWN与MENTIONED_UNCLEAR
valid_df = df[df['pregnant_included'].isin(['INCLUDED', 'EXCLUDED'])]

# Inclusion rate by phase
Stats = (
    valid_df.groupby('phase_category')['pregnant_included']
    .apply(lambda x: (x == 'INCLUDED').mean() * 100)
    .sort_values(ascending=False)
)

#热图数据
heatmap_data = (
    valid_df.groupby(['disease_category', 'phase_category'])['pregnant_included']
    .apply(lambda x: (x == 'INCLUDED').mean() * 100)
    .unstack()
)



#绘图
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
df['pregnant_included'].value_counts().plot(
    kind='pie',
    autopct='%1.1f%%',
    colors=['#66b3ff', '#ff9999', '#ffcc99', '#cccccc']
)
plt.title('Pregnancy Inclusion Status Distribution')
plt.ylabel('')
plt.subplot(1, 2, 2)
Stats.plot(kind='bar', color='skyblue', edgecolor='black')
plt.ylabel('Inclusion Rate(%)')
plt.title('Inclusion Rate by Study Phase')
plt.tight_layout()
plt.show()


#热力图
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', fmt='.1f')
plt.title('Pregnancy Inclusion Across Disease Categories and Phases')
plt.xlabel('Study Phase')
plt.ylabel('Disease Category')
plt.tight_layout()
plt.show()

#保存处理后的数据
df.to_csv(Output, index=False)
print(f"\nProcessed dataset saved to {Output}")
print("\nAnalysis completed.")
