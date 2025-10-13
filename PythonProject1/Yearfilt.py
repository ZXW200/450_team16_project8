import pandas as pd
import os

# 输入/输出路径
input_path = r"merged.csv"
output_path = r"merged_1993_2023.csv"

# 读取数据
df = pd.read_csv(input_path, encoding="utf-8")

# 转换日期
df["Date registration"] = pd.to_datetime(df["Date registration"], errors="coerce", dayfirst=True)

# 提取年份
df["Year"] = df["Date registration"].dt.year

# 筛选 1993–2023
filtered = df[(df["Year"] >= 1993) & (df["Year"] <= 2023)]

# 仅当路径里有目录时才创建
output_dir = os.path.dirname(output_path)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)

# 保存结果
filtered.to_csv(output_path, index=False, encoding="utf-8-sig")

print("success:", output_path)
print("result:", len(filtered))
