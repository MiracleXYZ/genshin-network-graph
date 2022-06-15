import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from utils import add_fullscreen, get_html_path, get_node_options

st.set_page_config(page_title="Character Network Graph", page_icon="🌍")

df_chars = pd.read_pickle("./data/characters.pickle")
df_text = pd.read_pickle("./data/voice_text.pickle")

# for traveler
df_chars.loc[df_chars["Name"] == "Traveler", "Element"] = "Traveler"

st.write("# Network Graph of Genshin Impact Characters")

elements = sorted(df_chars["Element"].drop_duplicates().tolist())
regions = sorted(df_chars["Region"].drop_duplicates().tolist())

filter_mode = st.selectbox(
    "Filter Mode",
    (
        "Weak Mode (unselected targets are shown translucent)",
        "Strict Mode (unselected targets are hidden)",
    ),
    index=0,
    help="Try it out yourself if you're not sure!",
)
selected_elements = st.multiselect("Select Element(s)", elements, default=elements)
selected_regions = st.multiselect("Select Region(s)", regions, default=regions)
selected_characters = df_chars[
    (df_chars["Element"].isin(selected_elements))
    & (df_chars["Region"].isin(selected_regions))
]["Name"].tolist()

if filter_mode.startswith("Strict"):
    df_text = df_text[
        (df_text["Source"].isin(selected_characters))
        & (df_text["Target"].isin(selected_characters))
    ]
else:
    df_text = df_text[df_text["Source"].isin(selected_characters)]


if len(df_text) == 0:
    st.write("No data found. Select elements and regions to start with.")
else:
    gs_net = Network(height="600px", width="100%", directed=True)

    gs_net.barnes_hut()

    for idx, row in df_text.iterrows():
        src = row["Source"]
        dst = row["Target"]
        w = row["Sentiment"]

        if src == dst:
            continue

        gs_net.add_node(
            src,
            src,
            title=src,
            **get_node_options(src, df_chars, selected_characters=selected_characters),
        )
        gs_net.add_node(
            dst,
            dst,
            title=dst,
            **get_node_options(dst, df_chars, selected_characters=selected_characters),
        )
        gs_net.add_edge(src, dst, value=w)

    gs_net.toggle_physics(True)

    with open("./options.json", "r") as f:
        gs_net.set_options(f.read())

    path = os.path.join(
        get_html_path(), 'genshin_network.html'
    )
    gs_net.show(path)
    add_fullscreen(path)
    html_file = open(path, "r", encoding="utf-8")

    components.html(html_file.read(), height=600)
    st.write(
        """\
## 💡 Tips

1. It may take a while to load the network graph. Please be patient.
2. Click on the graph and press "F" to toggle fullscreen.
3. Graph physics is on. Feel free to drag some characters and see how it goes.
4. The initialization is random. If you want a different layout, just refresh the page or toggle an option and then toggle back.\
"""
    )
