import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

# ===== 0. 路径与数据 =====
os.makedirs("CleanedDataPlt", exist_ok=True)
df = pd.read_csv("CleanedData/cleaned_ictrp.csv")

# 目标与特征
y = df["results_posted"].astype(int)
feat_cat = ["phase","study_type","sponsor_category","income_level"]
X = df[feat_cat].copy()

# 预处理 + 模型
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), feat_cat)])
pipe = Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=2000))]).fit(X, y)

# 系数与特征名
names = pipe.named_steps["pre"].get_feature_names_out()
coef  = pipe.named_steps["lr"].coef_.ravel()
odds  = np.exp(coef)

coef_df = pd.DataFrame({"feature": names, "coef": coef, "odds_ratio": odds})
coef_df.sort_values("coef", ascending=False).to_csv(
    "CleanedDataPlt/sklearn_logit_coefficients.csv", index=False, encoding="utf-8-sig"
)
print("Top effects:\n", coef_df.sort_values("coef", ascending=False).head(10))
print("Bottom effects:\n", coef_df.sort_values("coef").head(10))

# ===== 3. 画图（横向条形图，按绝对值排序）=====
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Logistic Regression Coefficients by Variable Group\n(Categorical Variables Only)',
             fontsize=16, fontweight='bold')

# 定义变量组
groups = {
    'Phase': 'cat__phase_',
    'Study Type': 'cat__study_type_',
    'Sponsor Category': 'cat__sponsor_category_',
    'Income Level': 'cat__income_level_'
}

axes_flat = axes.flatten()

for idx, (group_name, prefix) in enumerate(groups.items()):
    ax = axes_flat[idx]

    # 筛选该组的特征
    mask = [n.startswith(prefix) for n in names]
    group_names = names[mask]
    group_coef = coef[mask]
    group_odds = odds[mask]

    if len(group_names) == 0:
        ax.text(0.5, 0.5, 'No features', ha='center', va='center', fontsize=12)
        ax.set_title(group_name, fontweight='bold', fontsize=12)
        ax.axis('off')
        continue

    # 简化名称（去掉前缀）
    simple = [n.replace(prefix, '') for n in group_names]

    # 按系数排序
    sort_idx = np.argsort(group_coef)
    simple = np.array(simple)[sort_idx]
    group_coef_sorted = group_coef[sort_idx]
    group_odds_sorted = group_odds[sort_idx]

    # 颜色：绿色=正效应，红色=负效应
    colors = ['#d62728' if c < 0 else '#2ecc71' for c in group_coef_sorted]

    # 绘制横向柱状图
    bars = ax.barh(range(len(simple)), group_coef_sorted, color=colors,
                   alpha=0.8, edgecolor='black', linewidth=1.2)

    # 添加参考线（x=0）
    ax.axvline(0, color='black', linewidth=1.5, linestyle='--', alpha=0.5)

    # 设置Y轴标签
    ax.set_yticks(range(len(simple)))
    ax.set_yticklabels(simple, fontsize=9)

    # 设置X轴标签和标题
    ax.set_xlabel('Coefficient', fontsize=11, fontweight='bold')
    ax.set_title(group_name, fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 添加OR值标签
    for i, (bar, or_val) in enumerate(zip(bars, group_odds_sorted)):
        x_pos = bar.get_width()
        if abs(x_pos) > 0.05:  # 只显示较大的系数
            if x_pos > 0:
                # 正系数，标签在右边
                ax.text(x_pos + max(group_coef_sorted) * 0.02, i, f'{or_val:.2f}',
                        va='center', fontsize=9, fontweight='bold')
            else:
                # 负系数，标签在左边
                ax.text(x_pos + min(group_coef_sorted) * 0.02, i, f'{or_val:.2f}',
                        va='center', ha='right', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig("CleanedDataPlt/categorical_only_by_group.png", dpi=300, bbox_inches='tight')
print("Saved: CleanedDataPlt/categorical_only_by_group.png")
plt.show()
