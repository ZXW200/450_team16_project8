import pandas as pd

files = [
    r"data\Chagas_disease.csv",
    r"data\cysticercosis.csv",
    r"data\Human_African_trypanosomiasis.csv",
    r"data\Leprosy.csv",
    r"data\Lymphatic_filariasis.csv",
    r"data\Onchocerciasis.csv",
    r"data\Schistosomiasis.csv",
    r"data\Soil_transmitted_helminthiases.csv",
    r"data\Taeniasis.csv",
    r"data\Trachoma.csv",
    r"data\Visceral_leishmaniasis.csv",
    r"data\Yaws.csv"
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
output_path = r"merged.csv"
merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"finish: {output_path}")


