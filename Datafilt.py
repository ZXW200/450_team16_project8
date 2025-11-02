import pandas as pd
import os
import re
os.makedirs("CleanedData", exist_ok=True)
# 国家代码映射表先获取的表根据表的代码填 Country code mapping
COUNTRY_CODE = {
    'BRA': 'Brazil','IND': 'India', 'ARG': 'Argentina','KEN': 'Kenya','TZA': 'Tanzania','ETH': 'Ethiopia','CIV': 'Côte d\'Ivoire',
    'UGA': 'Uganda','ESP': 'Spain','USA': 'United States','BGD': 'Bangladesh','SDN': 'Sudan','CHN': 'China','BOL': 'Bolivia','COL': 'Colombia',
    'SEN': 'Senegal','NLD': 'Netherlands','GBR': 'United Kingdom','LAO': 'Laos','CHE': 'Switzerland','PHL': 'Philippines','KHM': 'Cambodia','VNM': 'Vietnam',
    'MEX': 'Mexico','NPL': 'Nepal','DEU': 'Germany','FRA': 'France','ZWE': 'Zimbabwe','BFA': 'Burkina Faso','MDG': 'Madagascar', 'IDN': 'Indonesia',
    'ZMB': 'Zambia', 'EGY': 'Egypt', 'GHA': 'Ghana','GAB': 'Gabon', 'CHL': 'Chile', 'MOZ': 'Mozambique', 'THA': 'Thailand','CAN': 'Canada','ECU': 'Ecuador',
    'TLS': 'Timor-Leste','FJI': 'Fiji','LKA': 'Sri Lanka','GTM': 'Guatemala','BEL': 'Belgium','GNB': 'Guinea-Bissau', 'MWI': 'Malawi','SLB': 'Solomon Islands','RWA': 'Rwanda',
    'HTI': 'Haiti','NER': 'Niger','PER': 'Peru','VEN': 'Venezuela','LBR': 'Liberia','AUS': 'Australia','COD': 'DR Congo','HND': 'Honduras',
    'CMR': 'Cameroon','ZAF': 'South Africa','MLI': 'Mali','SLV': 'El Salvador','MRT': 'Mauritania'
}
#世界收入分类 World bank classification
income_map = {
    "Low": ['BFA','MDG','MOZ','TZA','KEN','ETH','UGA','ZWE','MWI','RWA','NER','LBR','COD','SDN','HTI','MRT','GNB','MLI'],
    "Lower middle": ['IND','BGD','PHL','VNM','IDN','EGY','GHA','ZMB','CMR','NPL','KHM','LAO','LKA','TLS','HND','SLV','SEN','SLB'],
    "Upper middle": ['CHN','BRA','MEX','COL','THA','ZAF','PER','ECU','GAB','ARG','VEN','BOL','CIV','GTM','FJI'],
    "High": ['USA','GBR','DEU','FRA','ESP','NLD','CHE','CAN','AUS','BEL','CHL']
}
# 赞助商分类 Sponsor classification
def classify_categories(sponsor_name):
    #根据赞助商名称分类为：政府、工业界、非营利组织或其他
    if pd.isna(sponsor_name) or str(sponsor_name).upper() in ['UNKNOWN', '']:
        return "Unknown"
    sponsor_upper = str(sponsor_name).upper()

    government_keywords = ['MINISTRY', 'GOVERNMENT', 'NATIONAL INSTITUTE', 'CDC', 'NIH', 'DEPARTMENT', 'COUNCIL']
    industry_keywords = ['PHARMA', 'INC', 'CORP', 'LTD', 'LLC', 'DIVISION', 'LIMITED', 'KGAA']
    nonprofit_keywords = ['UNIVERSITY', 'HOSPITAL', 'FOUNDATION', 'INTERNATIONAL', 'NGO', 'TRUST', 'WHO',
                          'ORGANISATION',
                          'INSTITUTE', 'INSTITUTIONAL', 'ACADEMY', 'DRUGS FOR NEGLECTED DISEASES INITIATIVE',
                          'DRUGS FOR NEGLECTED DISEASES', 'SCHOOL', 'ACADEMIC', 'IDRI', 'PATH']

    if any(k in sponsor_upper for k in government_keywords):
        return "Government"
    if any(k in sponsor_upper for k in industry_keywords):
        return "Industry"
    if any(k in sponsor_upper for k in nonprofit_keywords):
        return "Non-profit"
    return "Other"

# 读取原始数据 Read raw data
file_path = "ictrp_data.csv"
df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")
print(f"raw data: {len(df)} 条")

# 处理日期字段 Process date fields
date_fields = ['date_registration', 'date_enrollment']
for field in date_fields:
    if field in df.columns:
        df[field] = pd.to_datetime(df[field], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')
# 提取注册年份 Extract registration year
df["Year"] = pd.to_datetime(df["date_registration"], format='%Y-%m-%d', errors="coerce").dt.year

# 清理HTML标签函数 Clean HTML tags function
def clean_html_tags(text):
    if pd.isna(text):
        return text
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\\r\\n', ' ').replace('\\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None

#清除所选列名的html标签
html_fields = [ "inclusion_criteria", "exclusion_criteria","primary_outcome","secondary_outcome"]
for field in html_fields:
    if field in df.columns:
        df[field] = df[field].apply(clean_html_tags)




# # print("\n异常值检测...")
outliers_removed = 0
# 检测样本量异常值 Check sample size outliers 最大1000000最小大于0
if 'target_sample_size' in df.columns:
    df['target_sample_size'] = pd.to_numeric(df['target_sample_size'], errors='coerce')
    before = len(df)
    df = df[(df['target_sample_size'].isna()) |
            ((df['target_sample_size'] > 0) & (df['target_sample_size'] <= 1000000))]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"样本量异常: 删除 {removed} 条")

# 年龄验证 Age validation
def validate_age(age_text):
    if pd.isna(age_text):
        return True
    age_text = str(age_text).lower()
    numbers = re.findall(r'\d+', age_text)
    if not numbers:
        return True
    age = int(numbers[0])
    if 'year' in age_text or 'y'or'Y' in age_text:#年最大等于120 最小大于等于0
        return 0 <= age <= 120
    elif 'month' in age_text or 'm'or'M' in age_text:#120*12 = 1440
        return 0 <= age <= 1440
    elif 'day' in age_text or 'week' in age_text:
        return True
    return 0 <= age <= 120

# 检测年龄异常值 Check age outliers
# 检查年龄逻辑是否合理 Check age logic validity
if 'inclusion_age_min' in df.columns and 'inclusion_age_max' in df.columns:
    before = len(df)
    # 检查最小和最大年龄都有效
    df = df[df['inclusion_age_min'].apply(validate_age)]
    df = df[df['inclusion_age_max'].apply(validate_age)]
    removed = before - len(df)
    outliers_removed += removed
print(f"deleted in total {outliers_removed} ")
#
# print("\n删除敏感信息列...")
sensitive_fields = ['contact_affiliation', 'secondary_sponsor', 'web_address', 'results_url_link']
removed_fields = []
for field in sensitive_fields:
    if field in df.columns:
        df = df.drop(field, axis=1)
        removed_fields.append(field)

if removed_fields:
    print(f"Delete: {', '.join(removed_fields)}")

# print("\n填充空值...")
fill_fields = ["standardised_condition", "countries", "primary_sponsor", "phase", "study_type"]
for field in fill_fields:
    if field in df.columns:
        df[field] = df[field].fillna("Unknown")

if "results_ind" in df.columns:
    df["results_ind"] = df["results_ind"].fillna("No")

if "target_sample_size" in df.columns:
    median_value = df["target_sample_size"].median()
    df["target_sample_size"] = df["target_sample_size"].fillna(median_value)
    print(f"Fill in missing values of sample size with median: {median_value}")
# 赞助商分类 Sponsor classification
df["sponsor_category"] = df["primary_sponsor"].apply(classify_categories)
##世界收入分类 Worldbank Classification
df["income_level"] = df["country_codes"].apply(map_income)
#统计赞助商分类占比
all_sponsor_counts = df["sponsor_category"].value_counts()
print("\nSponsor Category Classification:")
for category, count in all_sponsor_counts.items():
    print(f"  {category}: {count} ({count / len(df) * 100:.1f}%)")

# 统计各国实验数量
if 'country_codes' in df.columns:
    # 处理多国家情况进行统计（只统计指定的国家）
    country_list = []
    for codes in df['country_codes'].dropna():
        codes_str = str(codes).strip()
        if '|' in codes_str:
            codes = [c.strip() for c in codes_str.split('|')]
        else:
            codes = [codes_str]

        # 只添加在字典中的国家
        for code in codes:
            code = code.upper()
            if code in COUNTRY_CODE:
                country_list.append(COUNTRY_CODE[code])

    country_counts = pd.Series(country_list).value_counts()
    # 保存完整的国家统计
    country_counts.to_csv("CleanedData/country_statistics.csv", header=['count'], index_label='country', encoding="utf-8-sig")
    print(f"\nTotal countries with trials: {len(country_counts)}")

df["results_posted"] = df["results_ind"].str.upper().str.strip() == "YES"
published_df = df[df["results_posted"] == True].copy()
if 'country_codes' in published_df.columns:
    published_country_list = []
    for codes in published_df['country_codes'].dropna():
        codes_str = str(codes).strip()
        if '|' in codes_str:
            codes = [c.strip() for c in codes_str.split('|')]
        else:
            codes = [codes_str]

        # 只添加在字典中的国家
        for code in codes:
            code = code.upper()
            if code in COUNTRY_CODE:
                published_country_list.append(COUNTRY_CODE[code])

    published_country_counts = pd.Series(published_country_list).value_counts()
    published_country_counts.to_csv(f"CleanedData/published_country_statistics.csv",header=['count'], index_label='country', encoding="utf-8-sig")
print(f"\nPublished: {len(published_df)} ({len(published_df) / len(df) * 100:.1f}%)")
print(f"Unpublished: {len(df) - len(published_df)} ({(len(df) - len(published_df)) / len(df) * 100:.1f}%)")

df.to_csv("CleanedData/cleaned_ictrp.csv", index=False, encoding="utf-8-sig")
published_df.to_csv("CleanedData/published_trials.csv", index=False, encoding="utf-8-sig")

# 根据 pregnant_participants 字段筛选孕妇相关试验
if 'pregnant_participants' in df.columns:
    pregnant_trials = df[df['pregnant_participants'].str.upper().str.strip() == 'INCLUDED'].copy()
    pregnant_trials.to_csv("CleanedData/pregnant_trials.csv", index=False, encoding="utf-8-sig")
    print(f"Pregnant Trials: {len(pregnant_trials)}")
else:
    print("Warning: 'pregnant_participants' column not found in data")
    pregnant_trials = pd.DataFrame()

print("\nData Cleaning Completed!")
print(f"Time Range: {int(df['Year'].min())} - {int(df['Year'].max())}")
print(f"Total Trials: {len(df)}")
