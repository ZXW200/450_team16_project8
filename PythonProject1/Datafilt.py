import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score


# 1. 缺失值处理

def clean_missing_values(df):
    #数值列用均值填充，日期列转datetime
    df = df.copy()
    # print(" Start clean_missing_values")

    if "Date registration" in df.columns:
        df["Date registration"] = pd.to_datetime(df["Date registration"], errors="coerce", dayfirst=True)
        df["Year"] = df["Date registration"].dt.year
        # print("Converted Date registration to datetime, added Year")

    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="ignore")
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].fillna(df[c].mean())
            # print(f"Filled NaN in column {c} with mean")

    # print(" Finished clean_missing_values")
    return df


# 2. 特征选择

def prepare_features(df):
    #只保留数值列作为特征，构造标签 y，并返回特征名
    # print("[DEBUG] Start prepare_features")

    if "results yes no" in df.columns:
        y = df["results yes no"].astype(str).str.strip().str.lower().map(
            {"yes": 1, "no": 0, "1": 1, "0": 0, "true": 1, "false": 0}
        ).fillna(0).astype(int)
        # print(" Using results yes no as target y")
    else:
        y = df["results summary"].notna().astype(int)
        # print(" Using results summary as target y")

    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    X = df[num_cols].copy()

    # print(f"Selected {len(num_cols)} numeric features")
    return X, y, num_cols


# 3. 标准化

def build_model():
    #构造 pipeline: 标准化 + 逻辑回归
    # print("Building model pipeline (StandardScaler + LogisticRegression)")
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))
    ])
    return pipe


# 4. 特征可视化
def plot_feature_importance(feature_names, coefs, top_n=20, save_path="feature_importance.png"):
        imp = pd.DataFrame({
            "Feature": feature_names,
            "Coef": coefs,
            "AbsCoef": np.abs(coefs)
        }).sort_values("AbsCoef", ascending=False).head(top_n)

        plt.figure(figsize=(10, max(4, 0.45 * len(imp))))
        sns.barplot(x="AbsCoef", y="Feature", data=imp)
        plt.xlabel("|Coefficient| (on standardized features)")
        plt.ylabel("Feature")
        plt.title(f"Top {len(imp)} Feature Importances (Logistic Regression)")
        plt.tight_layout()
        plt.savefig(save_path, dpi=160)  # 保存图片
        plt.show()  # 新增：显示图片
        plt.close()

        print(f"Saved: {save_path}")
        print("\n=== Top feature importances ===")
        print(imp.assign(Sign=np.sign(imp["Coef"])))



# 5. 训练 & 评估

def train_and_evaluate(X, y, feature_names):
    # print("[DEBUG] Start train_and_evaluate")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    # print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")

    model = build_model()
    model.fit(X_train, y_train)
    # print("Model training finished")

    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    if hasattr(model.named_steps["clf"], "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        print("ROC-AUC:", roc_auc_score(y_test, y_proba))

    coefs = model.named_steps["clf"].coef_[0]
    plot_feature_importance(feature_names, coefs, top_n=20, save_path="feature_importance.png")

    # print("Finished train_and_evaluate")


# main

if __name__ == "__main__":
    # print("Start main pipeline")

    df = pd.read_csv("merged.csv", on_bad_lines="skip")
    df_clean = clean_missing_values(df)
    X, y, feature_names = prepare_features(df_clean)

    print("特征维度:", X.shape)
    print("标签分布:\n", y.value_counts())

    train_and_evaluate(X, y, feature_names)

    # print("End main pipeline")
