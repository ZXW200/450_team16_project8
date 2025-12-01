import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

#数据文件读取
df = pd.read_csv('CleanedData/cleaned_ictrp.csv')

#判断孕妇是否被纳入研究
#三个地方判别：专门标记、纳入、排除
def check(row):
    # 先看专门标记
    preg_mark = str(row.get('pregnant_participants', '')).strip().upper()
    # 有明确标记直接使用
    if preg_mark == 'INCLUDED':
        return 'INCLUDED'
    if preg_mark == 'EXCLUDED':
        return 'EXCLUDED'
    
    #没明确标记就查文本
    inc = str(row.get('inclusion_criteria', ''))
    exc = str(row.get('exclusion_criteria', ''))
    all_text = (inc + ' ' + exc).lower()
    
    #检查是否提到孕妇相关词汇
    preg_words = ['pregnant', 'pregnancy', 'gestation', 
                 'lactating', 'breastfeeding', 'childbearing']
    
    #没提到则返回未知
    has_preg = any(word in all_text for word in preg_words)
    if not has_preg:
        return 'UNKNOWN'
    
    #检查排除的情况
    exclude_patterns = ['exclud.*pregnant', 'no pregnant', 'not pregnant',
                       'non.pregnant', 'contraindicated.*pregnant']
    
    for pat in exclude_patterns:
        if re.search(pat, all_text):
            return 'EXCLUDED'
    
    #检查纳入的情况
    include_patterns = ['include.*pregnant', 'pregnant.*include', 
                       'pregnant.*allow', 'pregnant.*eligible']
    
    for pat in include_patterns:
        if re.search(pat, all_text):
            return 'INCLUDED'
    
    #提到了但不明确
    return 'MENTIONED_UNCLEAR'

#应用判断函数
df['preg_status'] = df.apply(check, axis=1)

#分析明确标记了包含或排除的研究
df_clear = df[df['preg_status'].isin(['INCLUDED', 'EXCLUDED'])]

#观测不同疾病类型的情况，选研究数量最多的前15种疾病分析
disease_counts = df_clear['standardised_condition'].value_counts()
top_diseases = disease_counts.head(15).index

df_top = df_clear[df_clear['standardised_condition'].isin(top_diseases)]

#计算每种疾病的孕妇纳入比例
def calc_incl_rate(group):
    #group是某个疾病的所有研究
    included = (group == 'INCLUDED').sum()
    total = len(group)
    return (included / total) * 100

#按疾病分组计算
incl_rates = df_top.groupby('standardised_condition')['preg_status'].apply(calc_incl_rate)
incl_rates = incl_rates.sort_values(ascending=False)

#交叉表反映具体数量
cross_table = pd.crosstab(df_top['standardised_condition'], df_top['preg_status'])



#总体情况饼图
fig1, ax1 = plt.subplots(figsize=(6, 6))

#计算各状态的数量
status_counts = df['preg_status'].value_counts()

#饼图设置
colors = ['#66b3ff', '#ff9999', '#ffcc99', '#99ff99']

ax1.pie(status_counts.values, 
        labels=status_counts.index, 
        autopct='%1.1f%%', 
        colors=colors)

ax1.set_title('All Studies Pregnancy Participation')
plt.tight_layout()
plt.show()

#按疾病分析的情况
fig2, axes = plt.subplots(1, 2, figsize=(17, 6))

#纳入率条形图
bars = axes[0].bar(incl_rates.index, incl_rates.values, color='salmon', alpha=0.75)

#在柱子上标出百分比
for bar in bars:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width() / 2, 
                height + 0.5, 
                f'{height:.1f}%', 
                ha='center', 
                va='bottom',
                fontsize=9)

axes[0].set_title('Pregnancy Inclusion Rate by Disease Type (Top 15)')
axes[0].set_ylabel('Inclusion Rate (%)')
axes[0].tick_params(axis='x', rotation=45)

#纳入vs排除数量对比
cross_table.plot(kind='bar', ax=axes[1], color=['lightcoral', 'lightgreen'])
axes[1].set_title('Pregnancy Inclusion vs Exclusion by Disease Type')
axes[1].set_ylabel('Number of Studies')
axes[1].legend(['Excluded', 'Included'])
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

#打印关键统计数据
print(f"Total studies: {len(df)}")
print(f"Studies with clear pregnancy status: {len(df_clear)}")
print("\nPregnancy status distribution:")
print(df['preg_status'].value_counts())
print("\nTop 5 diseases by inclusion rate:")
print(incl_rates.head())