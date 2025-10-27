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


