from CleanData import COUNTRY_CODE
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
df = pd.read_csv("CleanedData/cleaned_ictrp.csv", encoding="utf-8")
os.makedirs("CleanedData", exist_ok=True)
os.makedirs("CleanedDataPlt", exist_ok=True)
G = nx.Graph()

multi_country_trials = 0

# 遍历每个试验 Traversal Experiment
for idx, row in df.iterrows():
    if pd.isna(row['country_codes']):
        continue

    # 提取国家代码 get country codes
    codes_str = str(row['country_codes']).strip().upper()
    if '|' in codes_str:
        codes = [c.strip() for c in codes_str.split('|')]
    else:
        codes = [codes_str]

    # 转换为国家名称 turn to country names
    countries = []
    for code in codes:
        if code in COUNTRY_CODE:
            countries.append(COUNTRY_CODE[code])

    # 如果有多个国家，说明是合作试验 
    #If multiple countries are involved, it indicates a collaborative trial.
    if len(countries) >= 2:
        multi_country_trials += 1
        # 在这些国家之间建立连接
        #Establishing connections between these countries
        for i in range(len(countries)):
            for j in range(i+1, len(countries)):
                # 如果边已存在，增加权重；否则创建新边
                #If the edge already exists, increase the weight; otherwise, create a new edge.
                if G.has_edge(countries[i], countries[j]):
                    G[countries[i]][countries[j]]['weight'] += 1
                else:
                    G.add_edge(countries[i], countries[j], weight=1)

print(f"Have{multi_country_trials} multi-country trials in total.")
print(f"Have{G.number_of_nodes()} countries in the network.")
print(f"Have{G.number_of_edges()} collaborative connections in the network.")


# print("step 2")

# 计算每个国家的度（合作伙伴数量）
#calculate degree for each country (number of partners)
degree_dict = dict(G.degree())

# 计算加权度（总合作次数）
#calculate weighted degree (total number of collaborations)
weighted_degree = {}
for node in G.nodes():
    total_weight = 0
    for neighbor in G.neighbors(node):#Iterate through all neighbors and accumulate their weights.
                                    #遍历当前nodecountry的所有邻居，并累加它们的权重。
        total_weight += G[node][neighbor]['weight']
    weighted_degree[node] = total_weight

# 计算中心性（哪个国家最核心）
#calculate centrality (which country is the most central)
if len(G.nodes()) > 0:
    betweenness = nx.betweenness_centrality(G)

    # 创建结果表格
    # Create result table
    network_stats = pd.DataFrame({
        'Country': list(G.nodes()),
        'Number of partners': [degree_dict[n] for n in G.nodes()],#合作伙伴数
        'Total number of partnerships': [weighted_degree[n] for n in G.nodes()],#总合作次数
        'Mediation centrality': [betweenness[n] for n in G.nodes()]#中介中心性
    })

    # 按合作伙伴数排序
    # sort by number of partners
    network_stats = network_stats.sort_values('Number of partners', ascending=False)

    # 保存结果
    #save results
    network_stats.to_csv("CleanedData/network_statistics.csv", index=False, encoding="utf-8-sig")
    # print("Finished")
