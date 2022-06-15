import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from sklearn import manifold, preprocessing
from sklearn.pipeline import make_pipeline
from utils import (add_fullscreen, get_html_path, get_node_options,
                   get_node_options_dish, remove_duplicates)

st.set_page_config(page_title="Food Preferences", page_icon="🍴")

st.write(
    """\
# Food Preferences

This part of analysis is derived from an event called [Spices From the West](https://genshin-impact.fandom.com/wiki/Spices_From_the_West), where you can invite characters to eat some of the dishes you made. After trying the meal, characters will respond due to their preferences, which can be divided into three categories: Like (+1), Neutral (0), and Dislike (-1).

Based on this data, we can calculate the cosine similarity between characters' preferences, and then visualize our results.
"""
)

st.write("## Similarity of Characters")

df_chars = pd.read_pickle("./data/characters.pickle")
df_dishes = pd.read_pickle("./data/spices_dishes.pickle")
df_sim_chars = pd.read_pickle("./data/spices_sim_chars.pickle")
df_sim_dishes = pd.read_pickle("./data/spices_sim_dishes.pickle")
df_scores = pd.read_pickle("./data/spices_scores.pickle")

df_vectors = (
    df_scores.groupby(["name", "dish"]).mean()["score"].unstack().fillna(0).astype(int)
)
df_sim_chars = remove_duplicates(df_sim_chars)
df_sim_dishes = remove_duplicates(df_sim_dishes)

gs_net = Network(height="600px", width="100%", directed=False)
gs_net.barnes_hut()

pipe = make_pipeline(
    preprocessing.StandardScaler(),
    manifold.TSNE(n_components=2, init="pca", learning_rate="auto"),
)
embed_chars_array = pipe.fit_transform(df_vectors)
embed_chars = pd.DataFrame(
    embed_chars_array, index=df_vectors.index, columns=["x", "y"]
)

for idx, row in embed_chars.iterrows():
    gs_net.add_node(
        idx,
        x=float(row["x"]),
        y=float(row["y"]),
        title=idx,
        label=idx,
        **get_node_options(idx, df_chars, size=35)
    )

for idx, row in df_sim_chars.iterrows():
    if row["Source"] == row["Target"]:
        continue

    gs_net.add_edge(
        row["Source"],
        row["Target"],
        value=abs(row["Similarity"]),
        color="#22C55E" if row["Similarity"] > 0 else "#EF4444",
        physics=False,
    )

with open("./options_embed.json", "r") as f:
    gs_net.set_options(f.read())

path = os.path.join(get_html_path(), "food_preferences_chars.html")
gs_net.show(path)
add_fullscreen(path)
html_file = open(path, "r", encoding="utf-8")
components.html(html_file.read(), height=600)

st.write("### Similar Preference TOP 5")

df_rank = (
    df_sim_chars[df_sim_chars["Source"] != df_sim_chars["Target"]]
    .sort_values("Similarity", ascending=False)
    .reset_index(drop=True)
    .head(5)
)

df_rank.index += 1
st.dataframe(df_rank)

st.write("### Opposite Preference TOP 5")

df_rank = (
    df_sim_chars[df_sim_chars["Source"] != df_sim_chars["Target"]]
    .sort_values("Similarity", ascending=True)
    .reset_index(drop=True)
    .head(5)
)

df_rank.index += 1
st.dataframe(df_rank)

st.write('## Similarity of Dishes')

gs_net = Network(height="600px", width="100%", directed=False)
gs_net.barnes_hut()
embed_dishes_array = pipe.fit_transform(df_vectors.T)
embed_dishes = pd.DataFrame(
    embed_dishes_array, index=df_vectors.columns, columns=["x", "y"]
)

for idx, row in embed_dishes.iterrows():
    gs_net.add_node(
        idx,
        x=float(row["x"]),
        y=float(row["y"]),
        title=idx,
        label=idx,
        **get_node_options_dish(idx, df_dishes, size=35)
    )


for idx, row in df_sim_dishes.iterrows():
    if row["Source"] == row["Target"]:
        continue

    gs_net.add_edge(
        row["Source"],
        row["Target"],
        value=abs(row["Similarity"]),
        color="#22C55E" if row["Similarity"] > 0 else "#EF4444",
        physics=False,
    )

with open("./options_embed.json", "r") as f:
    gs_net.set_options(f.read())

path = os.path.join(get_html_path(), "food_preferences_dishes.html")
gs_net.show(path)
add_fullscreen(path)
html_file = open(path, "r", encoding="utf-8")
components.html(html_file.read(), height=600)

st.write("### Highest Similarity TOP 5")

df_rank = (
    df_sim_dishes[df_sim_dishes["Source"] != df_sim_dishes["Target"]]
    .sort_values("Similarity", ascending=False)
    .reset_index(drop=True)
    .head(5)
)

df_rank.index += 1
st.dataframe(df_rank)

st.write("### Lowest Similarity TOP 5")

df_rank = (
    df_sim_dishes[df_sim_dishes["Source"] != df_sim_dishes["Target"]]
    .sort_values("Similarity", ascending=True)
    .reset_index(drop=True)
    .head(5)
)

df_rank.index += 1
st.dataframe(df_rank)
