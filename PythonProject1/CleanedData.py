import pandas as pd
# 1. 读取数据
# print("Step 1: 读取数据...")
df = pd.read_csv('merged_1993_2023.csv', encoding='utf-8', low_memory=False)
# print(f"原始数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 2. 删除重复和缺失
# print("\nStep 2: 删除重复和缺失...")
# 根据试验ID删除重复记录
before_dup = len(df)
df = df.drop_duplicates(subset=['TrialID'], keep='first')
# print(f"删除重复记录: {before_dup - len(df)} 条")

# 删除缺少关键字段的记录
before_missing = len(df)
df = df[df['TrialID'].notna() & df['Year'].notna()]
# print(f"删除缺失记录: {before_missing - len(df)} 条")
# print(f"剩余记录: {len(df)} 条")

# 3. 填充缺失值
# print("\nStep 3: 填充缺失值...")
# 对分类变量，用'Unknown'填充缺失值
categorical_cols = ['Condition', 'Countries', 'Primary sponsor', 'Phase',
                    'Study type', 'Recruitment Status']
missing_counts = {}
for col in categorical_cols:
    if col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            missing_counts[col] = missing_count
        df[col] = df[col].fillna('Unknown')
if 'results yes no' in df.columns:
  df['results yes no']= df['results yes no'].fillna('No')
# if missing_counts:
#     for col, count in missing_counts.items():
#         print(f"   {col}: 填充 {count} 个缺失值")
# else:
#     # print("   分类变量无缺失值")

# 对数值变量，用中位数填充缺失值
if 'Target size' in df.columns:
    target_missing = df['Target size'].isna().sum()
    df['Target size'] = pd.to_numeric(df['Target size'], errors='coerce')
    median_val = df['Target size'].median()
    df['Target size'] = df['Target size'].fillna(median_val)
    # print(f"Target size: 填充 {target_missing} 个缺失值 (中位数={median_val:.0f})")

#4. 提取儿童信息
# print("\nStep 4: 提取儿童纳入信息...")


def extract_min_age(age_str):

    if pd.isna(age_str):
        return None

    age_str = str(age_str).lower()

    # 提取数字（取前3位，避免提取过多）
    number_str = ''.join([c for c in age_str if c.isdigit()][:3])
    if not number_str:
        return None

    age = int(number_str)

    # 根据单位转换为年
    if 'month' in age_str:
        return age / 12
    elif 'day' in age_str:
        return age / 365
    elif 'week' in age_str:
        return age / 52

    # 默认认为是年
    return age


# 检查字段是否存在
if 'Inclusion agemin' not in df.columns:
    # print("'Inclusion agemin' 字段不存在")
    df['Includes_Children'] = 'Unknown'
else:
    # 计算最小年龄
    df['Min_Age'] = df['Inclusion agemin'].apply(extract_min_age)

    # 判断是否包含儿童（<18岁）
    df['Includes_Children'] = df['Min_Age'].apply(
        lambda x: 'Yes' if pd.notna(x) and x < 18 else 'No' if pd.notna(x) else 'Unknown'
    )

    # 统计结果
    children_yes = (df['Includes_Children'] == 'Yes').sum()
    children_no = (df['Includes_Children'] == 'No').sum()
    children_unknown = (df['Includes_Children'] == 'Unknown').sum()
    # print(f"包含儿童: {children_yes} 项 ({children_yes / len(df) * 100:.1f}%)")
    # print(f"不包含儿童: {children_no} 项 ({children_no / len(df) * 100:.1f}%)")
    # print(f"未知: {children_unknown} 项 ({children_unknown / len(df) * 100:.1f}%)")

# ========== 5. 提取孕妇信息 ==========
# print("\nStep 5: 提取孕妇纳入信息...")

# 检查字段是否存在
if 'Inclusion Criteria' not in df.columns and 'Exclusion Criteria' not in df.columns:
    # print("   ⚠ 警告: 纳入/排除标准字段不存在")
    df['Includes_Pregnant'] = 'Unknown'
else:
    # 定义孕妇相关关键词
    pregnant_keywords = ['pregnant', 'pregnancy', 'gravid', 'gestation', 'expecting']

    # 获取纳入和排除标准（转为小写便于匹配）
    inclusion = df['Inclusion Criteria'].fillna('').str.lower()
    exclusion = df['Exclusion Criteria'].fillna('').str.lower()

    # 检查纳入标准中是否提到孕妇
    includes_pregnant = inclusion.apply(lambda x: any(k in x for k in pregnant_keywords))

    # 检查排除标准中是否提到孕妇
    excludes_pregnant = exclusion.apply(lambda x: any(k in x for k in pregnant_keywords))

    # 判断是否包含孕妇
    # 逻辑：纳入标准提到 -> Yes；只在排除标准提到 -> No；都没提到 -> Unknown
    df['Includes_Pregnant'] = 'Unknown'
    df.loc[includes_pregnant, 'Includes_Pregnant'] = 'Yes'
    df.loc[excludes_pregnant & ~includes_pregnant, 'Includes_Pregnant'] = 'No'

    # 统计结果
    pregnant_yes = (df['Includes_Pregnant'] == 'Yes').sum()
    pregnant_no = (df['Includes_Pregnant'] == 'No').sum()
    pregnant_unknown = (df['Includes_Pregnant'] == 'Unknown').sum()
    # print(f"包含孕妇: {pregnant_yes} 项 ({pregnant_yes / len(df) * 100:.1f}%)")
    # print(f"不包含孕妇: {pregnant_no} 项 ({pregnant_no / len(df) * 100:.1f}%)")
    # print(f"未知: {pregnant_unknown} 项 ({pregnant_unknown / len(df) * 100:.1f}%)")

# ========== 6. 保存互斥分类数据 ==========
# print("\nStep 6: 保存数据...")

# 完整的清洗后数据
df.to_csv('CleanedData/cleaned_ntd_data.csv', index=False, encoding='utf-8')
# print(f"完整数据: cleaned_ntd_data.csv ({len(df)} 行)")

# 只包含儿童（不包含孕妇）
children_only = df[(df['Includes_Children'] == 'Yes') & (df['Includes_Pregnant'] != 'Yes')]
children_only.to_csv('CleanedData/trials_with_children_only.csv', index=False, encoding='utf-8')
# print(f"只包含儿童: trials_with_children_only.csv ({len(children_only)} 行)")

# 只包含孕妇（不包含儿童）
pregnant_only = df[(df['Includes_Pregnant'] == 'Yes') & (df['Includes_Children'] != 'Yes')]
pregnant_only.to_csv('CleanedData/trials_with_pregnant_only.csv', index=False, encoding='utf-8')
# print(f"只包含孕妇: trials_with_pregnant_only.csv ({len(pregnant_only)} 行)")

# 同时包含儿童和孕妇
both = df[(df['Includes_Children'] == 'Yes') & (df['Includes_Pregnant'] == 'Yes')]
both.to_csv('CleanedData/trials_with_both.csv', index=False, encoding='utf-8')
# print(f"同时包含: trials_with_both.csv ({len(both)} 行)")

# ========== 7. 数据质量总结 ==========
# print("\n" + "=" * 60)
# print("数据清洗完成！")
# print("=" * 60)
# print(f"最终数据量: {len(df)} 条记录")
# print(f"数据完整性: {(1 - df.isna().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%")
# print(f"\n脆弱人群分布（互斥）:")
# print(f"  只包含儿童: {len(children_only)} ({len(children_only) / len(df) * 100:.1f}%)")
# print(f"  只包含孕妇: {len(pregnant_only)} ({len(pregnant_only) / len(df) * 100:.1f}%)")
# print(f"  同时包含: {len(both)} ({len(both) / len(df) * 100:.1f}%)")
# print(f"  总计: {len(children_only) + len(pregnant_only) + len(both)} ({(len(children_only) + len(pregnant_only) + len(both)) / len(df) * 100:.1f}%)")

