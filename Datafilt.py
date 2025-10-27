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
