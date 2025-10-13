import pandas as pd

files = [
    r"D:\PychamProject\PythonProject1\data\Chagas_disease.csv",
    r"D:\PychamProject\PythonProject1\data\cysticercosis.csv",
    r"D:\PychamProject\PythonProject1\data\Human_African_trypanosomiasis.csv",
    r"D:\PychamProject\PythonProject1\data\Leprosy.csv",
    r"D:\PychamProject\PythonProject1\data\Lymphatic_filariasis.csv",
    r"D:\PychamProject\PythonProject1\data\Onchocerciasis.csv",
    r"D:\PychamProject\PythonProject1\data\Schistosomiasis.csv",
    r"D:\PychamProject\PythonProject1\data\Soil_transmitted_helminthiases.csv",
    r"D:\PychamProject\PythonProject1\data\Taeniasis.csv",
    r"D:\PychamProject\PythonProject1\data\Trachoma.csv",
    r"D:\PychamProject\PythonProject1\data\Visceral_leishmaniasis.csv",
    r"D:\PychamProject\PythonProject1\data\Yaws.csv"
]

dfs = []

for f in files:
    try:
        df = pd.read_csv(f, on_bad_lines="skip", encoding="utf-8")
        dfs.append(df)
        print(f"Read Success: {f}")
    except Exception as e:
        print(f"read {f} error: {e}")

if not dfs:
    raise ValueError("No such file or directory")

merged_df = pd.concat(dfs, ignore_index=True)

# 去掉重复列
merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

# 输出路径
output_path = r"D:\PychamProject\PythonProject1\merged_clean_v3.csv"
merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"finish: {output_path}")
