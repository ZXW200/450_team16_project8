import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

# 读取原始数据
SRC = "merged_1993_2023.csv"

OUT_NO_CONTACTS = r"FD\clean_no_contacts.csv"
OUT_IMPUTED = r"FD\clean_no_contacts_imputed.csv"
OUT_ONLY_CHILD = r"FD\trials_only_children.csv"
OUT_ONLY_PREG = r"FD\trials_only_pregnant.csv"
OUT_BOTH = r"FD\trials_children_and_pregnant.csv"
OUT_NEITHER = r"FD\trials_neither.csv"

df = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False)

# 删除不需要的联系人列
contact_cols = [
    "Contact Firstname", "Contact Lastname", "Contact Address", "Contact Email",
    "Contact Tel", "Contact Affiliation",
    "Ethics Contact Name", "Ethics Contact Address", "Ethics Contact Phone", "Ethics Contact Email"
]
df = df.drop(columns=[c for c in contact_cols if c in df.columns])

# 保存删除联系人信息后的数据
df.to_csv(OUT_NO_CONTACTS, index=False, encoding="utf-8-sig")


def strip_html(s: str) -> str:
    # 去除html标签
    if pd.isna(s):
        return ""
    txt = str(s)
    # 把<br>换成空格
    txt = txt.replace("<br>", " ").replace("<BR>", " ").replace("<br/>", " ").replace("<br />", " ")
    # 去掉所有<>标签
    while "<" in txt and ">" in txt:
        start = txt.find("<")
        end = txt.find(">")
        if start < end:
            txt = txt[:start] + " " + txt[end + 1:]
        else:
            break
    # 把&nbsp;等换成空格
    txt = txt.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    # 把多个空格合并成一个
    while "  " in txt:
        txt = txt.replace("  ", " ")
    return txt.strip()


def parse_age_years(val):
    # 把年龄都转成年
    if pd.isna(val):
        return np.nan
    try:
        return float(val)
    except:
        s = str(val).lower()
        # 提取数字
        num_str = ""
        for char in s:
            if char.isdigit() or char == ".":
                num_str += char
        if not num_str:
            return np.nan
        num = float(num_str)

        # 判断单位
        if "year" in s or "yr" in s:
            return num
        elif "month" in s or "mo" in s:
            return num / 12.0
        elif "day" in s:
            return num / 365.0
        else:
            return num  # 默认就是年


# 解析年龄
df["age_min_years"] = df.get("Inclusion agemin", pd.Series(np.nan, index=df.index)).apply(parse_age_years)

# 处理缺失值
num_cols = df.select_dtypes(include=["number"]).columns.tolist()
if "age_min_years" not in num_cols and "age_min_years" in df.columns:
    num_cols.append("age_min_years")

num_df = df[num_cols].copy() if num_cols else pd.DataFrame()

# 清理数值列
if not num_df.empty:
    num_df = num_df.dropna(axis=1, how="all")
    std = num_df.std()
    num_df = num_df.drop(columns=std[std == 0].index)
    num_cols = num_df.columns.tolist()

# KNN填充
if num_cols:
    scaler = StandardScaler()
    num_scaled = scaler.fit_transform(num_df)

    imputer = KNNImputer(n_neighbors=5)
    num_imputed_scaled = imputer.fit_transform(num_scaled)

    num_imputed = scaler.inverse_transform(num_imputed_scaled)
    num_imputed_df = pd.DataFrame(num_imputed, columns=num_cols, index=df.index)

    df_imputed = df.copy()
    df_imputed[num_cols] = num_imputed_df[num_cols]
else:
    df_imputed = df.copy()

# 文本列填Unknown
for col in df_imputed.columns:
    if pd.api.types.is_string_dtype(df_imputed[col]):
        df_imputed[col] = df_imputed[col].fillna("Unknown")

df_imputed.to_csv(OUT_IMPUTED, index=False, encoding="utf-8-sig")

# 准备纳入排除标准
incl = df_imputed.get("Inclusion Criteria", pd.Series("", index=df_imputed.index)).apply(strip_html).str.lower()
excl = df_imputed.get("Exclusion Criteria", pd.Series("", index=df_imputed.index)).apply(strip_html).str.lower()

# 关键词匹配
keywords_children = ["child", "children", "paediatric", "pediatric", "adolescent", "infant", "juvenile", "neonate",
                     "newborn", "youth"]
keywords_pregnancy = ["pregnan", "gestat", "prenatal", "antenatal"]

age_min_years = df_imputed["age_min_years"]

if "results yes no" in df_imputed.columns:
    df_imputed["results yes no"] = df_imputed["results yes no"].fillna("No")


# 判断是不是儿童试验
def has_keyword(text, keywords):
    for kw in keywords:
        if kw in text:
            return True
    return False


children_incl_kw = incl.apply(lambda x: has_keyword(x, keywords_children))
children_excl_kw = excl.apply(lambda x: has_keyword(x, keywords_children))
children_age_flag = (age_min_years < 18).fillna(False)
children_flag = ((children_incl_kw | children_age_flag) & (~children_excl_kw))

# 判断是不是孕妇试验
preg_incl_kw = incl.apply(lambda x: has_keyword(x, keywords_pregnancy))
preg_excl_kw = excl.apply(lambda x: has_keyword(x, keywords_pregnancy))
pregnant_flag = preg_incl_kw & (~preg_excl_kw)

# 分类
only_children = df_imputed[children_flag & ~pregnant_flag].copy()
only_pregnant = df_imputed[pregnant_flag & ~children_flag].copy()
both = df_imputed[children_flag & pregnant_flag].copy()
neither = df_imputed[~(children_flag | pregnant_flag)].copy()

# 保存文件
only_children.to_csv(OUT_ONLY_CHILD, index=False, encoding="utf-8-sig")
only_pregnant.to_csv(OUT_ONLY_PREG, index=False, encoding="utf-8-sig")
both.to_csv(OUT_BOTH, index=False, encoding="utf-8-sig")
neither.to_csv(OUT_NEITHER, index=False, encoding="utf-8-sig")

# 打印结果
print("原始(去联系人后)总数:", df.shape[0])
print("缺失值处理后(记录不变):", df_imputed.shape[0])
print("仅儿童:", only_children.shape[0],
      "| 仅孕妇:", only_pregnant.shape[0],
      "| 同时:", both.shape[0],
      "| 都不涉及:", neither.shape[0])
print("四类合计:", only_children.shape[0] + only_pregnant.shape[0] + both.shape[0] + neither.shape[0])
print("已导出：")
print(" -", OUT_NO_CONTACTS)
print(" -", OUT_IMPUTED)
print(" -", OUT_ONLY_CHILD)
print(" -", OUT_ONLY_PREG)
print(" -", OUT_BOTH)
print(" -", OUT_NEITHER)