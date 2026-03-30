import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import squareform
from scipy.cluster import hierarchy

# ===============================
# PARAMETERS
# ===============================

ALPHA = 0.5   # weight node vs edge distance
LANGUAGES_TO_COMPARE = ["Man", "Blg", "It", "Fr", "Rm", "SC"]

# ===============================
# LOAD DATA
# ===============================

df = pd.read_excel("TableA_94_2025.xlsx")
# df.drop(df.columns[-5:], axis=1, inplace=True)

labels = df["Label"].dropna().tolist()
implications = df["Implicational Condition(s)"]

# ===============================
# BUILD BASE GRAPH (STRUCTURE)
# ===============================

base_graph = nx.DiGraph()
base_graph.add_nodes_from(labels)

for node, imp in zip(labels, implications):
    if not pd.notna(imp):
        continue
    imp = imp.translate({ord(k): " " for k in "()+-¬,−"})
    imp = imp.replace("or", " ")
    imp = imp.split()
    for n in imp:
        if n in base_graph.nodes:
            base_graph.add_edge(n, node)

# ===============================
# BUILD LANGUAGE GRAPHS
# ===============================

def build_language_graph(language):
    g = base_graph.copy()
    values = df[language]

    for node, val in zip(labels, values):
        if val == "+":
            g.nodes[node]["attr"] = 1
        elif val == "-":
            g.nodes[node]["attr"] = -1
        else:
            g.nodes[node]["attr"] = 0

    return g

language_graphs = {
    lang: build_language_graph(lang)
    for lang in LANGUAGES_TO_COMPARE
}

# ===============================
# DISTANCE FUNCTIONS
# ===============================

def node_distance(g1, g2):
    mismatches = sum(
        g1.nodes[n]["attr"] != g2.nodes[n]["attr"]
        for n in g1.nodes
    )
    return mismatches / g1.number_of_nodes()


def edge_distance(g1, g2):
    e1 = set(g1.edges())
    e2 = set(g2.edges())

    if len(e1 | e2) == 0:
        return 0.0

    return len(e1 ^ e2) / len(e1 | e2)


def graph_distance(g1, g2, alpha=ALPHA):
    return alpha * node_distance(g1, g2) + (1 - alpha) * edge_distance(g1, g2)


def graph_similarity(g1, g2, alpha=ALPHA):
    return 1 - graph_distance(g1, g2, alpha)

# ===============================
# BASE SIMILARITY MATRIX
# ===============================

print("=== BASE SIMILARITIES ===")
for i, l1 in enumerate(LANGUAGES_TO_COMPARE):
    for l2 in LANGUAGES_TO_COMPARE[i + 1:]:
        sim = graph_similarity(language_graphs[l1], language_graphs[l2])
        print(f"{l1} – {l2}: {sim:.3f}")

# ===============================
# BETWENNESS CENTRALITY
# ===============================

betweenness = nx.betweenness_centrality(base_graph, normalized=True)
ranked_nodes = sorted(betweenness, key=betweenness.get, reverse=True)

# ===============================
# SIMILARITY UNDER NODE REMOVAL
# ===============================

def similarity_decay(lang1, lang2, ranked_nodes):
    g1 = language_graphs[lang1]
    g2 = language_graphs[lang2]

    similarities = []
    removed_nodes = []

    for k in range(len(ranked_nodes)):
        remove = ranked_nodes[:k]

        g1_k = g1.copy()
        g2_k = g2.copy()

        g1_k.remove_nodes_from(remove)
        g2_k.remove_nodes_from(remove)

        if g1_k.number_of_nodes() == 0:
            break

        similarities.append(graph_similarity(g1_k, g2_k))

        if k == 0:
            removed_nodes.append("None")
        else:
            removed_nodes.append(ranked_nodes[k-1])

    return similarities, removed_nodes


# ===============================
# PLOT DECAY CURVES
# ===============================

plt.figure(figsize=(16, 8))

pairs = [
    ("Man", "Blg"), ("Man", "It"), ("Blg", "It"),
    ("Fr", "Blg"), ("Fr", "Man"), ("Fr", "It"),
    ("Fr", "Rm"), ("Rm", "Blg"), ("Rm", "It"), ("Rm", "Man"),
    ("SC", "Rm"), ("SC", "Blg"), ("SC", "It"), ("SC", "Man"), ("SC", "Fr")
]

# Colormap tab20 (20 colori distinti)
cmap = plt.get_cmap("tab20")
colors = cmap(np.linspace(0, 1, len(pairs)))

# Use first pair to get x-axis labels
sim_curve, x_labels = similarity_decay(pairs[0][0], pairs[0][1], ranked_nodes)

for i, (l1, l2) in enumerate(pairs):
    sim_curve, _ = similarity_decay(l1, l2, ranked_nodes)
    plt.plot(sim_curve, label=f"{l1}–{l2}", color=colors[i])

plt.xticks(
    ticks=range(len(x_labels)),
    labels=x_labels,
    rotation=90
)

plt.xlabel("Removed node (based on betweenness centrality)")
plt.ylabel("Similarity")
plt.title("Similarity decay under node removal (by node name)")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("similarity_betweenness.png")
plt.show()


def node_impact_analysis(lang1, lang2, ranked_nodes):
    """
    Computes the marginal similarity change caused by removing each node
    in betweenness order.
    """
    g1 = language_graphs[lang1]
    g2 = language_graphs[lang2]

    results = []

    prev_similarity = graph_similarity(g1, g2)

    removed = []

    for node in ranked_nodes:
        removed.append(node)

        g1_k = g1.copy()
        g2_k = g2.copy()

        g1_k.remove_nodes_from(removed)
        g2_k.remove_nodes_from(removed)

        if g1_k.number_of_nodes() == 0:
            break

        new_similarity = graph_similarity(g1_k, g2_k)
        delta = new_similarity - prev_similarity

        results.append({
            "node": node,
            "betweenness": betweenness[node],
            "similarity_before": prev_similarity,
            "similarity_after": new_similarity,
            "delta_similarity": delta
        })

        prev_similarity = new_similarity

    return pd.DataFrame(results)


pd.set_option("display.float_format", "{:.12f}".format)

impact_results = {}

for l1, l2 in pairs:
    df_impact = node_impact_analysis(l1, l2, ranked_nodes)
    impact_results[(l1, l2)] = df_impact

    print(f"\n=== Top impactful nodes for {l1}–{l2} ===")
    print(
        df_impact
        .sort_values("delta_similarity", key=abs, ascending=False)
        .head(20)[["node", "betweenness", "delta_similarity"]]
    )


def plot_node_impacts(df_impact, lang1, lang2, top_n=15):
    df_plot = (
        df_impact
        .sort_values("delta_similarity", key=abs, ascending=False)
        .head(top_n)
        .iloc[::-1]  # for horizontal plotting
    )

    plt.figure(figsize=(8, 6))
    plt.barh(df_plot["node"], df_plot["delta_similarity"])
    plt.axvline(0, linestyle="--")
    plt.xlabel("Δ Similarity")
    plt.title(f"Most impactful nodes: {lang1}–{lang2}")
    plt.tight_layout()
    plt.show()


# Example:
plot_node_impacts(impact_results[("Man", "Blg")], "Man", "Blg")
plot_node_impacts(impact_results[("Man", "It")], "Man", "It")
plot_node_impacts(impact_results[("Blg", "It")], "Blg", "It")
plot_node_impacts(impact_results[("Fr", "It")], "Fr", "It")
plot_node_impacts(impact_results[("Fr", "Rm")], "Fr", "Rm")
plot_node_impacts(impact_results[("Fr", "Blg")], "Fr", "Blg")
plot_node_impacts(impact_results[("Fr", "Man")], "Fr", "Man")
plot_node_impacts(impact_results[("Rm", "Blg")], "Rm", "Blg")
plot_node_impacts(impact_results[("Rm", "Man")], "Rm", "Man")
plot_node_impacts(impact_results[("Rm", "It")], "Rm", "It")
plot_node_impacts(impact_results[("SC", "Blg")], "SC", "Blg")
plot_node_impacts(impact_results[("SC", "Man")], "SC", "Man")
plot_node_impacts(impact_results[("SC", "It")], "SC", "It")
plot_node_impacts(impact_results[("SC", "Fr")], "SC", "Fr")
plot_node_impacts(impact_results[("SC", "Rm")], "SC", "Rm")


# ===============================
# FULL BETWENNESS CENTRALITY TABLE
# ===============================

betweenness_df = (
    pd.DataFrame({
        "node": list(betweenness.keys()),
        "betweenness": list(betweenness.values())
    })
    .sort_values("betweenness", ascending=False)
    .reset_index(drop=True)
)

print("\n=== Betweenness centrality for all nodes ===")
print(betweenness_df)



