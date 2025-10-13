import pandas as pd
import os

# 输入/输出路径
input_path = r"D:\PychamProject\PythonProject1\merged.csv"
output_path = r"D:\PychamProject\PythonProject1\merged_1993_2023.csv"

# 读取数据
df = pd.read_csv(input_path, encoding="utf-8")

# 转换日期
df["Date registration"] = pd.to_datetime(df["Date registration"], errors="coerce", dayfirst=True)

# 提取年份
df["Year"] = df["Date registration"].dt.year

# 筛选 1993–2023
filtered = df[(df["Year"] >= 1993) & (df["Year"] <= 2023)]

# 保存结果
os.makedirs(os.path.dirname(output_path), exist_ok=True)
filtered.to_csv(output_path, index=False, encoding="utf-8-sig")

print("success:", output_path)
print("result:", len(filtered))

