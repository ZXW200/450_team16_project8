import pandas as pd
import os
import re


# 国家关键词映射字典
COUNTRY_KEYWORDS = {
    'Brazil': ['BRAZIL', 'BRASIL', 'FIOCRUZ', 'OSWALDO CRUZ', 'SAO PAULO',
               'RIO DE JANEIRO', 'MINAS GERAIS', 'BAHIA'],
    'United States': ['USA', 'UNITED STATES', 'U.S.', 'AMERICAN', 'NIH',
                      'CDC', 'FDA', 'NATIONAL INSTITUTE', 'WASHINGTON',
                      'CALIFORNIA', 'NEW YORK', 'BOSTON', 'TEXAS'],
    'India': ['INDIA', 'INDIAN', 'NEW DELHI', 'MUMBAI', 'BANARAS',
              'BANGALORE', 'HYDERABAD', 'CHENNAI', 'KOLKATA'],
    'United Kingdom': ['UK', 'UNITED KINGDOM', 'BRITISH', 'LONDON',
                       'OXFORD', 'CAMBRIDGE', 'SCOTLAND', 'WALES'],
    'Netherlands': ['NETHERLANDS', 'DUTCH', 'AMSTERDAM', 'LEIDEN',
                    'ROTTERDAM', 'UTRECHT'],
    'Spain': ['SPAIN', 'SPANISH', 'BARCELONA', 'MADRID', 'VALENCIA'],
    'France': ['FRANCE', 'FRENCH', 'PARIS', 'LYON', 'MARSEILLE'],
    'Germany': ['GERMANY', 'GERMAN', 'BERLIN', 'MUNICH', 'HAMBURG'],
    'Switzerland': ['SWITZERLAND', 'SWISS', 'GENEVA', 'ZURICH', 'BERN'],
    'Belgium': ['BELGIUM', 'BELGIAN', 'BRUSSELS', 'ANTWERP'],
    'Argentina': ['ARGENTINA', 'ARGENTINE', 'BUENOS AIRES'],
    'Ethiopia': ['ETHIOPIA', 'ETHIOPIAN', 'ADDIS ABABA'],
    'Kenya': ['KENYA', 'KENYAN', 'NAIROBI', 'MOMBASA'],
    'Uganda': ['UGANDA', 'UGANDAN', 'KAMPALA'],
    'Tanzania': ['TANZANIA', 'TANZANIAN', 'DAR ES SALAAM'],
    'South Africa': ['SOUTH AFRICA', 'SOUTH AFRICAN', 'CAPE TOWN', 'JOHANNESBURG'],
    'China': ['CHINA', 'CHINESE', 'BEIJING', 'SHANGHAI', 'GUANGZHOU'],
    'Japan': ['JAPAN', 'JAPANESE', 'TOKYO', 'OSAKA', 'KYOTO'],
    'Australia': ['AUSTRALIA', 'AUSTRALIAN', 'SYDNEY', 'MELBOURNE'],
    'Canada': ['CANADA', 'CANADIAN', 'TORONTO', 'MONTREAL', 'VANCOUVER'],
}

# 特殊组织映射
SPECIAL_ORGS = {
    'DRUGS FOR NEGLECTED DISEASES': 'International',
    'WHO': 'International',
    'WORLD HEALTH ORGANIZATION': 'International',
    'DNDI': 'International',
    'BAYER': 'Germany',
    'NOVARTIS': 'Switzerland',
    'PFIZER': 'United States',
    'GSK': 'United Kingdom',
    'GLAXOSMITHKLINE': 'United Kingdom',
}

# 疾病缩写映射
DISEASE_ABBREVIATIONS = {
    'Chagas Disease': 'CD',
    'Schistosomiasis': 'SCH',
    'Visceral Leishmaniasis': 'VL',
    'Soil-Transmitted Helminthiases': 'STH',
    'Schistosomiasis|Soil-Transmitted Helminthiases': 'SCH+STH',
    'Chagas Disease|Schistosomiasis': 'CD+SCH',
    'Visceral Leishmaniasis|Schistosomiasis': 'VL+SCH'
}


# ============================================================================
# 辅助函数定义
# ============================================================================

def identify_country_sponsor(sponsor_name):
    """识别赞助商所属国家"""
    if pd.isna(sponsor_name):
        return 'Unknown'

    sponsor_name = str(sponsor_name).upper()

    # 先检查特殊组织
    for org, country in SPECIAL_ORGS.items():
        if org in sponsor_name:
            return country

    # 检查国家关键词
    for country, keywords in COUNTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in sponsor_name:
                return country

    return 'Other'


# ============================================================================
# 开始数据清洗
# ============================================================================

# print("Start")

# 步骤1：读取数据
# print("1. 读取数据")

# 读取ICTRP数据文件
file_path = "ictrp_data.csv"
df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")
# print(f"成功读取: {file_path}")
print(f"original: {len(df)} , {len(df.columns)} ")

# 步骤2：统一日期格式并提取年份
# print("2. 统一日期格式并提取年份")

# 需要处理的日期字段
date_fields = ['date_registration', 'date_enrollment',
               'results_date_completed', 'results_date_posted']

for field in date_fields:
    if field in df.columns:
        # 统一转换为标准日期格式 (YYYY-MM-DD)
        df[field] = pd.to_datetime(df[field], format='%Y-%m-%d', errors='coerce')
        # 转换为字符串格式统一显示
        df[field] = df[field].dt.strftime('%Y-%m-%d')
        # print(f"  ✓ {field}")

# 从注册日期提取年份
df["date_registration_dt"] = pd.to_datetime(df["date_registration"], errors="coerce")
df["Year"] = df["date_registration_dt"].dt.year
df = df.drop('date_registration_dt', axis=1)  # 删除临时列

# 只保留1993-2023年的数据
df = df[(df["Year"] >= 1993) & (df["Year"] <= 2023)]
print(f"93-23: {len(df)} ")

# 步骤3：删除重复和缺失
# print("3. 删除重复和缺失")

# 删除重复的试验ID
before = len(df)
df = df.drop_duplicates(subset=["trial_id"], keep="first")
print(f"Del rep: {before - len(df)} ")

# 删除没有ID或年份的记录
before = len(df)
df = df[df["trial_id"].notna() & df["Year"].notna()]
print(f"Del Missing: {before - len(df)} ")


# 步骤4：清洗HTML标签
# print("4. 清洗HTML标签")

def clean_html_tags(text):
    """清除HTML标签和特殊字符"""
    if pd.isna(text):
        return text

    text = str(text)

    # 移除<br>标签
    text = re.sub(r'<br\s*/?>', ' ', text)

    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除转义字符
    text = text.replace('\\r\\n', ' ').replace('\\n', ' ').replace('\\r', ' ')

    # 替换HTML实体
    text = text.replace('&apos;', "'").replace('&quot;', '"')
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')

    # 清理多余空格
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text if text else None


# 需要清洗HTML的文本字段
html_fields = [
    "study_title",
    "inclusion_criteria",
    "exclusion_criteria",
    "primary_outcome",
    "secondary_outcome",
    "intervention",
    "original_condition",
    "standardised_condition"
]

for field in html_fields:
    if field in df.columns:
        df[field] = df[field].apply(clean_html_tags)

# print(f"已清洗 {len([f for f in html_fields if f in df.columns])} 个文本字段的HTML标签")


# 步骤5：标准化国家名称
# print("5. 标准化国家名称")

# 国家名称标准化映射表
country_mapping = {
    # 常见缩写
    'USA': 'United States',
    'US': 'United States',
    'U.S.': 'United States',
    'U.S.A.': 'United States',
    'UK': 'United Kingdom',
    'U.K.': 'United Kingdom',
    'UAE': 'United Arab Emirates',

    # 非标准名称
    "Cote d'Ivoire": 'Ivory Coast',
    "Côte d'Ivoire": 'Ivory Coast',
    'Congo (Brazzaville)': 'Republic of the Congo',
    'Congo (Kinshasa)': 'Democratic Republic of the Congo',
    'Congo, The Democratic Republic of the': 'Democratic Republic of the Congo',

    # 其他变体
    'Russian Federation': 'Russia',
    'Republic of Korea': 'South Korea',
    'Korea, Republic of': 'South Korea',
    "Democratic People's Republic of Korea": 'North Korea',
    'Viet Nam': 'Vietnam',
    'Iran, Islamic Republic of': 'Iran',
    'Venezuela, Bolivarian Republic of': 'Venezuela',
    'Tanzania, United Republic of': 'Tanzania',
    'Syrian Arab Republic': 'Syria',
    "Lao People's Democratic Republic": 'Laos',
    'Myanmar': 'Myanmar',
    'Burma': 'Myanmar',
}


def standardize_country(country_text):
    """标准化国家名称"""
    if pd.isna(country_text):
        return country_text

    country_text = str(country_text).strip()

    # 处理多个国家的情况（用分号或逗号分隔）
    if ';' in country_text or ',' in country_text:
        separator = ';' if ';' in country_text else ','
        countries = [c.strip() for c in country_text.split(separator)]
        standardized = [country_mapping.get(c, c) for c in countries]
        return ';'.join(standardized)

    # 单个国家
    return country_mapping.get(country_text, country_text)


if 'countries' in df.columns:
    before_unique = df['countries'].nunique()
    df['countries'] = df['countries'].apply(standardize_country)
    after_unique = df['countries'].nunique()
    # print(f"国家名称标准化: {before_unique} → {after_unique} 个不同国家")

if 'country_codes' in df.columns:
    df['country_codes'] = df['country_codes'].str.strip().str.upper()

# 步骤6：异常值检测和处理
# print("6. 异常值检测和处理")

outliers_removed = 0

# 6.1 样本量异常值检测
if 'target_sample_size' in df.columns:
    df['target_sample_size'] = pd.to_numeric(df['target_sample_size'], errors='coerce')

    # 删除不合理的样本量（<=0 或 >1000000）
    before = len(df)
    df = df[(df['target_sample_size'].isna()) |
            ((df['target_sample_size'] > 0) & (df['target_sample_size'] <= 1000000))]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"  样本量异常值: 删除 {removed} 条")


# 6.2 年龄异常值检测
def validate_age(age_text):
    """验证年龄是否合理"""
    if pd.isna(age_text):
        return True

    age_text = str(age_text).lower()

    # 提取数字
    numbers = re.findall(r'\d+', age_text)
    if not numbers:
        return True

    age = int(numbers[0])

    # 根据单位判断是否合理
    if 'year' in age_text or 'y' in age_text:
        return 0 <= age <= 120
    elif 'month' in age_text:
        return 0 <= age <= 1440  # 120年
    elif 'day' in age_text or 'week' in age_text:
        return True  # 天和周通常是合理的

    return 0 <= age <= 120


if 'inclusion_age_min' in df.columns:
    before = len(df)
    df = df[df['inclusion_age_min'].apply(validate_age)]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"  年龄异常值: 删除 {removed} 条")

# 6.3 日期逻辑异常检测
if 'date_registration' in df.columns and 'date_enrollment' in df.columns:
    date_reg = pd.to_datetime(df['date_registration'], errors='coerce')
    date_enroll = pd.to_datetime(df['date_enrollment'], errors='coerce')

    # 删除入组日期早于注册日期的记录（逻辑错误）
    before = len(df)
    invalid_dates = (date_enroll.notna()) & (date_reg.notna()) & (date_enroll < date_reg)
    df = df[~invalid_dates]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"  日期逻辑异常: 删除 {removed} 条")

print(f" del error{outliers_removed} ")
# 步骤7：删除联系人等敏感信息
# print("7. 删除联系人等敏感信息")

# 要删除的敏感字段列表
sensitive_fields = [
    'contact_affiliation',  # 联系人单位
    'secondary_sponsor',  # 次要赞助商（可能包含个人信息）
    'web_address',  # 网址（根据需求可选）
    'results_url_link',  # 结果链接
]

removed_fields = []
for field in sensitive_fields:
    if field in df.columns:
        df = df.drop(field, axis=1)
        removed_fields.append(field)


# 步骤8：填充空值
# print("8. 填充空值")

# 需要填充的字段
fill_fields = ["standardised_condition", "countries", "primary_sponsor",
               "phase", "study_type", "centre"]

# 用"Unknown"填充空值
for field in fill_fields:
    if field in df.columns:
        df[field] = df[field].fillna("Unknown")

# results_ind 用 "No" 填充
if "results_ind" in df.columns:
    df["results_ind"] = df["results_ind"].fillna("No")

# target_sample_size 用中位数填充
if "target_sample_size" in df.columns:
    middle_value = df["target_sample_size"].median()
    df["target_sample_size"] = df["target_sample_size"].fillna(middle_value)


# print("填充完成")

# 步骤9：判断是否包含儿童
# print("9. 判断是否包含儿童")

def get_age_in_years(age_text):
    """把年龄文本转换为数字（单位：年）"""
    if pd.isna(age_text):
        return None

    # 转为小写
    age_text = str(age_text).lower()

    # 提取数字
    numbers = ""
    for char in age_text:
        if char.isdigit():
            numbers += char

    if not numbers:
        return None

    age = int(numbers)

    # 转换单位
    if "month" in age_text:  # 月
        age = age / 12
    elif "week" in age_text:  # 周
        age = age / 52
    elif "day" in age_text:  # 天
        age = age / 365

    return age


# 计算最小年龄
if "inclusion_age_min" in df.columns:
    df["Min_Age"] = df["inclusion_age_min"].apply(get_age_in_years)

    # 判断是否包含儿童（小于18岁）
    df["Includes_Children"] = "Unknown"
    df.loc[df["Min_Age"] < 18, "Includes_Children"] = "Yes"
    df.loc[df["Min_Age"] >= 18, "Includes_Children"] = "No"

    yes_count = sum(df["Includes_Children"] == "Yes")
    no_count = sum(df["Includes_Children"] == "No")
    unknown_count = sum(df["Includes_Children"] == "Unknown")

    # print(f"包含儿童: {yes_count} 项")
    # print(f"不包含儿童: {no_count} 项")
    # print(f"未知: {unknown_count} 项")
else:
    df["Includes_Children"] = "Unknown"
    # print("未找到年龄字段")

# 步骤10：判断是否包含孕妇
# print("10. 判断是否包含孕妇")

# 孕妇相关关键词
pregnant_words = ["pregnant", "pregnancy", "gravid", "gestation", "expecting"]

if "inclusion_criteria" in df.columns and "exclusion_criteria" in df.columns:
    # 获取纳入和排除标准（转为小写）
    inclusion_text = df["inclusion_criteria"].fillna("").str.lower()
    exclusion_text = df["exclusion_criteria"].fillna("").str.lower()

    # 检查纳入标准中是否提到孕妇
    in_inclusion = inclusion_text.apply(
        lambda text: any(word in text for word in pregnant_words)
    )

    # 检查排除标准中是否提到孕妇
    in_exclusion = exclusion_text.apply(
        lambda text: any(word in text for word in pregnant_words)
    )

    # 判断逻辑
    df["Includes_Pregnant"] = "Unknown"
    df.loc[in_inclusion, "Includes_Pregnant"] = "Yes"
    df.loc[in_exclusion & ~in_inclusion, "Includes_Pregnant"] = "No"

    yes_count = sum(df["Includes_Pregnant"] == "Yes")
    no_count = sum(df["Includes_Pregnant"] == "No")
    unknown_count = sum(df["Includes_Pregnant"] == "Unknown")

    # print(f"包含孕妇: {yes_count} 项")
    # print(f"不包含孕妇: {no_count} 项")
    # print(f"未知: {unknown_count} 项")
else:
    df["Includes_Pregnant"] = "Unknown"
    # print("未找到纳入/排除标准字段")

# 步骤11：计算国家资助次数和疾病统计
# print("11. 计算国家资助次数和疾病统计")

# 添加赞助商国家字段 (使用顶部定义的函数和映射)
df['Sponsor_Country'] = df['primary_sponsor'].apply(identify_country_sponsor)

# 添加疾病缩写字段 (使用顶部定义的映射)
df['Disease_Abbr'] = df['standardised_condition'].map(DISEASE_ABBREVIATIONS)

# 统计国家资助次数和疾病
sponsor_country_counts = df['Sponsor_Country'].value_counts()
disease_counts = df['standardised_condition'].value_counts()

# print(f"识别出 {df['Sponsor_Country'].nunique()} 个资助来源")
# print(f"统计了 {df['standardised_condition'].nunique()} 种疾病")

# 步骤12：保存文件
# print("12. 保存文件")

# 创建保存文件夹
os.makedirs("CleanedData", exist_ok=True)

# 1. 保存完整数据
df.to_csv("CleanedData/cleaned_ictrp.csv", index=False, encoding="utf-8-sig")
# print(f"完整数据: {len(df)} 条")

# 2. 只包含儿童（不包含孕妇）
children_only = df[(df["Includes_Children"] == "Yes") &
                   (df["Includes_Pregnant"] != "Yes")]
children_only.to_csv("CleanedData/children_only.csv",
                     index=False, encoding="utf-8-sig")
# print(f"只包含儿童: {len(children_only)} 条")

# 3. 只包含孕妇（不包含儿童）
pregnant_only = df[(df["Includes_Pregnant"] == "Yes") &
                   (df["Includes_Children"] != "Yes")]
pregnant_only.to_csv("CleanedData/pregnant_only.csv",
                     index=False, encoding="utf-8-sig")
# print(f"只包含孕妇: {len(pregnant_only)} 条")

# 4. 同时包含儿童和孕妇
both = df[(df["Includes_Children"] == "Yes") &
          (df["Includes_Pregnant"] == "Yes")]
both.to_csv("CleanedData/Children_Pregnant.csv",
            index=False, encoding="utf-8-sig")
# print(f"同时包含儿童和孕妇: {len(both)} 条")

# 步骤13：生成统计报告
# print("13. 生成统计报告")

# 国家资助统计报告
sponsor_stats = df.groupby('Sponsor_Country').agg({
    'trial_id': 'count',
    'target_sample_size': ['mean', 'median'],
    'standardised_condition': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
}).round(2)
sponsor_stats.columns = ['Funding_Count', 'Avg_Sample_Size', 'Median_Sample_Size', 'Main_Disease']
sponsor_stats = sponsor_stats.sort_values('Funding_Count', ascending=False)
sponsor_stats.to_csv('CleanedData/sponsor_country_statistics.csv', encoding='utf-8-sig')

# 疾病统计报告
disease_stats = df.groupby('standardised_condition').agg({
    'trial_id': 'count',
    'target_sample_size': ['mean', 'median'],
    'Sponsor_Country': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
    'Includes_Children': lambda x: (x == 'Yes').sum()
}).round(2)
disease_stats.columns = ['Study_Count', 'Avg_Sample_Size', 'Median_Sample_Size', 'Main_Sponsor_Country',
                         'Children_Studies_Count']
disease_stats = disease_stats.sort_values('Study_Count', ascending=False)
disease_stats.to_csv('CleanedData/disease_statistics.csv', encoding='utf-8-sig')

# 国家-疾病交叉表
cross_tab = pd.crosstab(df['Sponsor_Country'], df['standardised_condition'])
cross_tab.to_csv('CleanedData/sponsor_disease_crosstab.csv', encoding='utf-8-sig')

# 结果汇总
print("\nResult")
print("\n" + "=" * 60)
print("Cleaned Finish！")
print("=" * 60)
print(f"Duration: {int(df['Year'].min())} - {int(df['Year'].max())}")
print(f"All: {len(df)}")
print(f"Only included Children: {len(children_only)} ")
print(f"Only included Pregnant: {len(pregnant_only)} ")
print(f"Both have Children and Pregnant: {len(both)} ")
for i, (country, count) in enumerate(sponsor_country_counts.items(), 1):
    print(f"  {i}. {country}: {count} ({count/len(df)*100:.1f}%)")
print("="*60)
for i, (disease, count) in enumerate(disease_counts.items(), 1):
    print(f"  {i}. {disease}: {count} ({count/len(df)*100:.1f}%)")
print("\nAll CleanedData saved in CleanedData/ ")

#赞助商分类
def classify_categories(sponsor_name):
    #分3类：Industry, Government, Non-profit
    if pd.isna(sponsor_name):
        return "Unknown"

    sponsor_upper = str(sponsor_name).upper()

    if sponsor_upper in ['UNKNOWN', '']:
        return "Unknown"

    government_keywords = [
        'MINISTRY', 'GOVERNMENT',
        'NATIONAL INSTITUTE', 'NATIONAL RESEARCH',
        'STATE INSTITUTE', 'PUBLIC HEALTH INSTITUTE',
        'NIAID', 'CDC', 'NIH', 'DEPARTMENT', 'COUNCIL',
        'FEDERAL INSTITUTE', 'RESEARCH COUNCIL','PUBLIQUE'
    ]

    # Industry（行业/商业）
    industry_keywords = [
        'PHARMA', 'BAYER', 'MERCK', 'ABBOTT', 'PFIZER', 'NOVARTIS',
        'GSK', 'SANOFI', 'ROCHE', 'BIOTECH',
        'INC', 'CORP', 'LTD', 'GMBH', ' AG', 'LLC','S.A','LIMITED'
    ]

    # Non-profit（非盈利）- 大学、医院、NGO、国际组织
    nonprofit_keywords = [
        # 基础
        'UNIVERSITY', 'HOSPITAL', 'FOUNDATION', 'ACADEMY',
        'INTERNATIONAL', 'INSTITUTE', 'ORGANIZATION', 'ORG','COLLEGE',
        'INSTITUTO','INSTITUTO NACIONAL ','SCHOOL','CAMPUS','UNIVERSIDAD', 'UNIVERSIDADE','UNIVERSITÉ','UNIVERSITÄT',

        # 联合国机构
        'WHO', 'WORLD HEALTH ORGANIZATION',
        'UNICEF', 'UNITED NATIONS CHILDREN',
        'UNDP', 'UNITED NATIONS DEVELOPMENT',
        'WORLD BANK',

        # 知名基金会
        'GATES FOUNDATION', 'BILL & MELINDA GATES', 'BMGF',
        'WELLCOME TRUST', 'WELLCOME',
        'ROCKEFELLER FOUNDATION',

        # 医疗NGO
        'DNDI', 'DRUGS FOR NEGLECTED DISEASES',
        'MSF', 'MEDECINS SANS FRONTIERES', 'DOCTORS WITHOUT BORDERS',
        'PATH',
        'TDR', 'SPECIAL PROGRAMME FOR RESEARCH AND TRAINING',

        # 疫苗和全球卫生
        'GAVI', 'VACCINE ALLIANCE',
        'GLOBAL FUND',
        'PEPFAR','IDRI',

        # 国际援助
        'USAID', 'DFID', 'CIDA',

        # 红十字会
        'RED CROSS', 'RED CRESCENT',

        # 通用词
        'NGO', 'NON-PROFIT', 'NONPROFIT', 'CHARITY', 'TRUST'
    ]

    # 优先级：Government > Industry > Non-profit
    # 首先检查Government（因为国家研究所优先级最高）
    if any(keyword in sponsor_upper for keyword in government_keywords):
        return "Government"

    if any(keyword in sponsor_upper for keyword in industry_keywords):
        return "Industry"

    if any(keyword in sponsor_upper for keyword in nonprofit_keywords):
        return "Non-profit"

    return "Other"


# 对所有赞助商分类
df["sponsor_category"] = df["primary_sponsor"].apply(classify_categories)

# 统计所有赞助商分类
all_sponsor_counts = df["sponsor_category"].value_counts()

print("\nAll Trials  Sponsor Classification :")
for category, count in all_sponsor_counts.items():
    pct = count / len(df) * 100
    print(f"  {category}: {count} ({pct:.1f}%)")

# 筛选已发表
if "results_ind" in df.columns:
    df["results_posted"] = df["results_ind"].str.upper().str.strip() == "YES"
else:
    df["results_posted"] = False

published_df = df[df["results_posted"] == True].copy()
unpublished_df = df[df["results_posted"] == False].copy()

print(f"\nPublished: {len(published_df)} ({len(published_df) / len(df) * 100:.1f}%)")
print(f"Unpublished: {len(unpublished_df)} ({len(unpublished_df) / len(df) * 100:.1f}%)")

# 统计已发表的赞助商分类
published_sponsor_counts = published_df["sponsor_category"].value_counts()
print("\nPublished Trials  - Sponsor Classification:")
for category, count in published_sponsor_counts.items():
    pct = count / len(published_df) * 100
    print(f"  {category}: {count} ({pct:.1f}%)")

# 计算各类赞助商的发表率
publication_rates = {}
for category in all_sponsor_counts.index:
    total_in_category = len(df[df["sponsor_category"] == category])
    published_in_category = len(published_df[published_df["sponsor_category"] == category])
    rate = (published_in_category / total_in_category * 100) if total_in_category > 0 else 0
    publication_rates[category] = {
        'total': total_in_category,
        'published': published_in_category,
        'rate': rate
    }

print("\nPublication Rate by Sponsor Category:")
for category, stats in publication_rates.items():
    print(f"{category}: {stats['published']}/{stats['total']} ({stats['rate']:.1f}%)")

# 创建输出目录
os.makedirs("/home/claude/sponsors_categories", exist_ok=True)

# 保存分类结果
df[['trial_id', 'primary_sponsor', 'sponsor_category', 'results_posted']].to_csv(r"CleanedData/all_trials_categories.csv",
    index=False, encoding="utf-8-sig")

