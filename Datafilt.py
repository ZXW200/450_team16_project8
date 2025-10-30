import pandas as pd
import os
import re

COUNTRY_KEYWORDS = {
    'Brazil': ['BRAZIL', 'BRASIL', 'FIOCRUZ', 'SAO PAULO'],
    'United States': ['USA', 'UNITED STATES', 'U.S.', 'NIH', 'CDC'],
    'India': ['INDIA', 'INDIAN', 'NEW DELHI', 'MUMBAI'],
    'United Kingdom': ['UK', 'UNITED KINGDOM', 'LONDON', 'OXFORD'],
    'Netherlands': ['NETHERLANDS', 'DUTCH', 'AMSTERDAM'],
    'Spain': ['SPAIN', 'SPANISH', 'BARCELONA', 'MADRID'],
    'France': ['FRANCE', 'FRENCH', 'PARIS'],
    'Germany': ['GERMANY', 'GERMAN', 'BERLIN'],
    'Switzerland': ['SWITZERLAND', 'SWISS', 'GENEVA'],
    'Belgium': ['BELGIUM', 'BELGIAN', 'BRUSSELS'],
}

SPECIAL_ORGS = {
    'DRUGS FOR NEGLECTED DISEASES': 'International',
    'WHO': 'International',
    'DNDI': 'International',
    'BAYER': 'Germany',
    'NOVARTIS': 'Switzerland',
    'PFIZER': 'United States',
    'GSK': 'United Kingdom',
}


def identify_country_sponsor(sponsor_name):
    if pd.isna(sponsor_name):
        return 'Unknown'
    sponsor_name = str(sponsor_name).upper()
    for org, country in SPECIAL_ORGS.items():
        if org in sponsor_name:
            return country
    for country, keywords in COUNTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in sponsor_name:
                return country
    return 'Other'


def classify_categories(sponsor_name):
    if pd.isna(sponsor_name) or str(sponsor_name).upper() in ['UNKNOWN', '']:
        return "Unknown"
    sponsor_upper = str(sponsor_name).upper()

    government_keywords = ['MINISTRY', 'GOVERNMENT', 'NATIONAL INSTITUTE', 'CDC', 'NIH', 'DEPARTMENT','COUNCIL']
    industry_keywords = ['PHARMA', 'INC', 'CORP', 'LTD', 'LLC','DIVISION','LIMITED','KGAA']
    nonprofit_keywords = ['UNIVERSITY', 'HOSPITAL', 'FOUNDATION', 'INTERNATIONAL', 'NGO', 'TRUST','WHO', 'ORGANISATION',
                          'INSTITUTE', 'INSTITUTIONAL','ACADEMY','DRUGS FOR NEGLECTED DISEASES INITIATIVE','DRUGS FOR NEGLECTED DISEASES','SCHOOL','ACADEMIC','IDRI','PATH']

    if any(k in sponsor_upper for k in government_keywords):
        return "Government"
    if any(k in sponsor_upper for k in industry_keywords):
        return "Industry"
    if any(k in sponsor_upper for k in nonprofit_keywords):
        return "Non-profit"
    return "Other"


file_path = "ictrp_data.csv"
df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")
print(f"raw data: {len(df)} 条")

date_fields = ['date_registration', 'date_enrollment', 'results_date_completed', 'results_date_posted']
for field in date_fields:
    if field in df.columns:
        df[field] = pd.to_datetime(df[field], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')

df["Year"] = pd.to_datetime(df["date_registration"], format='%Y-%m-%d', errors="coerce").dt.year



def clean_html_tags(text):
    if pd.isna(text):
        return text
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\\r\\n', ' ').replace('\\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None


html_fields = ["study_title", "inclusion_criteria", "exclusion_criteria", "standardised_condition"]
for field in html_fields:
    if field in df.columns:
        df[field] = df[field].apply(clean_html_tags)

country_mapping = {
    'USA': 'United States', 'US': 'United States', 'UK': 'United Kingdom',
    'Russian Federation': 'Russia', 'Viet Nam': 'Vietnam'
}


def standardize_country(country_text):
    if pd.isna(country_text):
        return country_text
    country_text = str(country_text).strip()
    if ';' in country_text or ',' in country_text:
        separator = ';' if ';' in country_text else ','
        countries = [c.strip() for c in country_text.split(separator)]
        return ';'.join([country_mapping.get(c, c) for c in countries])
    return country_mapping.get(country_text, country_text)


if 'countries' in df.columns:
    df['countries'] = df['countries'].apply(standardize_country)

# print("\n异常值检测...")
outliers_removed = 0

if 'target_sample_size' in df.columns:
    df['target_sample_size'] = pd.to_numeric(df['target_sample_size'], errors='coerce')
    before = len(df)
    df = df[(df['target_sample_size'].isna()) |
            ((df['target_sample_size'] > 0) & (df['target_sample_size'] <= 1000000))]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"  样本量异常: 删除 {removed} 条")


def validate_age(age_text):
    if pd.isna(age_text):
        return True
    age_text = str(age_text).lower()
    numbers = re.findall(r'\d+', age_text)
    if not numbers:
        return True
    age = int(numbers[0])
    if 'year' in age_text or 'y' in age_text:
        return 0 <= age <= 120
    elif 'month' in age_text:
        return 0 <= age <= 1440
    elif 'day' in age_text or 'week' in age_text:
        return True
    return 0 <= age <= 120


if 'inclusion_age_min' in df.columns:
    before = len(df)
    df = df[df['inclusion_age_min'].apply(validate_age)]
    removed = before - len(df)
    outliers_removed += removed
    # print(f"  年龄异常: 删除 {removed} 条")

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


def get_age_in_years(age_text):
    if pd.isna(age_text):
        return None
    age_text = str(age_text).lower()
    numbers = ''.join(c for c in age_text if c.isdigit())
    if not numbers:
        return None
    age = int(numbers)
    if "month" in age_text:
        age = age / 12
    elif "week" in age_text:
        age = age / 52
    elif "day" in age_text:
        age = age / 365
    return age


if "inclusion_age_min" in df.columns:
    df["Min_Age"] = df["inclusion_age_min"].apply(get_age_in_years)
    df["Includes_Children"] = "Unknown"
    df.loc[df["Min_Age"] < 18, "Includes_Children"] = "Yes"
    df.loc[df["Min_Age"] >= 18, "Includes_Children"] = "No"

pregnant_words = ["pregnant", "pregnancy", "gravid", "gestation"]
if "inclusion_criteria" in df.columns and "exclusion_criteria" in df.columns:
    inclusion_text = df["inclusion_criteria"].fillna("").str.lower()
    exclusion_text = df["exclusion_criteria"].fillna("").str.lower()
    in_inclusion = inclusion_text.apply(lambda t: any(w in t for w in pregnant_words))
    in_exclusion = exclusion_text.apply(lambda t: any(w in t for w in pregnant_words))
    df["Includes_Pregnant"] = "Unknown"
    df.loc[in_inclusion, "Includes_Pregnant"] = "Yes"
    df.loc[in_exclusion & ~in_inclusion, "Includes_Pregnant"] = "No"

df['Sponsor_Country'] = df['primary_sponsor'].apply(identify_country_sponsor)
df["sponsor_category"] = df["primary_sponsor"].apply(classify_categories)

all_sponsor_counts = df["sponsor_category"].value_counts()
print("\nSponsor Category Classification:")
for category, count in all_sponsor_counts.items():
    print(f"  {category}: {count} ({count / len(df) * 100:.1f}%)")

df["results_posted"] = df["results_ind"].str.upper().str.strip() == "YES"
published_df = df[df["results_posted"] == True].copy()

print(f"\nPublished: {len(published_df)} ({len(published_df) / len(df) * 100:.1f}%)")
print(f"Unpublished: {len(df) - len(published_df)} ({(len(df) - len(published_df)) / len(df) * 100:.1f}%)")

os.makedirs("CleanedData", exist_ok=True)

df.to_csv("CleanedData/cleaned_ictrp.csv", index=False, encoding="utf-8-sig")
published_df.to_csv("CleanedData/published_trials.csv", index=False, encoding="utf-8-sig")

children_only = df[(df["Includes_Children"] == "Yes") & (df["Includes_Pregnant"] != "Yes")]
pregnant_only = df[(df["Includes_Pregnant"] == "Yes") & (df["Includes_Children"] != "Yes")]
both = df[(df["Includes_Children"] == "Yes") & (df["Includes_Pregnant"] == "Yes")]

children_only.to_csv("CleanedData/children_only.csv", index=False, encoding="utf-8-sig")
pregnant_only.to_csv("CleanedData/pregnant_only.csv", index=False, encoding="utf-8-sig")
both.to_csv("CleanedData/Children_Pregnant.csv", index=False, encoding="utf-8-sig")

print("\nData Cleaning Completed!")
print(f"Time Range: {int(df['Year'].min())} - {int(df['Year'].max())}")
print(f"Total Trials: {len(df)}")
print(f"Children Only: {len(children_only)}")
print(f"Pregnant Only: {len(pregnant_only)}")
print(f"Children + Pregnant: {len(both)}")
