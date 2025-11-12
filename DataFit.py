import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import os
# 读取数据
# Load data
df = pd.read_csv("CleanedData/cleaned_ictrp.csv")
os.makedirs("CleanedDataPlt", exist_ok=True)
# 准备特征和目标变量
# Prepare features and target variable
features = ["phase", "study_type", "sponsor_category", "income_level"]
X = df[features]
y = df["results_posted"].astype(int)

# 转换分类变量为哑变量 log can only handle numerical input
# Convert categorical variables to dummy variables
X_encoded = pd.get_dummies(X, drop_first=True)

# 划分训练测试集
# Split train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)

# 训练逻辑回归模型
# Train logistic regression model
model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)

# 提取系数
# Extract coefficients
results = pd.DataFrame({
    "feature": X_encoded.columns,
    "coefficient": model.coef_[0],
})
results = results.sort_values("coefficient", ascending=False)
results.to_csv("CleanedData/logit_results.csv", index=False, encoding="utf-8-sig")

# 绘图
# Plotting
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Logistic Regression Coefficients', fontsize=16, fontweight='bold')

# 按变量类型分组绘图
# Group by variable type
groups = {
    'Phase': 'phase_',
    'Study Type': 'study_type_',
    'Sponsor': 'sponsor_category_',
    'Income Level': 'income_level_'
}

for i, (title, prefix) in enumerate(groups.items()):
    ax = axes.flatten()[i]
    
    # 筛选该组特征
    # Filter features for this group
    group_data = results[results['feature'].str.startswith(prefix)].copy()
    
    if len(group_data) == 0:
        continue
    
    # 去掉前缀
    # Remove prefix
    group_data['short_name'] = group_data['feature'].str.replace(prefix, '')
    group_data = group_data.sort_values('coefficient')
    
    # 画条形图
    # Draw bar chart
    colors = ['#d62728' if x < 0 else '#2ecc71' for x in group_data['coefficient']]
    ax.barh(group_data['short_name'], group_data['coefficient'], 
            color=colors, alpha=0.75, edgecolor='black', linewidth=0.5)
    ax.axvline(0, color='black', linestyle='--', linewidth=1.5)
    ax.set_xlabel('Coefficient ', fontsize=11)
    ax.set_title(title, fontweight='bold', fontsize=12)
    ax.grid(axis='x', alpha=0.3)
    
    # 添加图例
    # Add legend
    if i == 0:
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', alpha=0.75, label='Positive'),
            Patch(facecolor='#d62728', alpha=0.75, label='Negative')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

# 保存图片
# Save plot
plt.tight_layout()
plt.savefig("CleanedDataPlt/coefficients_plot.png", dpi=300, bbox_inches='tight')
# plt.show()
