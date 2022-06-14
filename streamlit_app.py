import os
import platform

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from pyvis.network import Network

df_chars = pd.read_pickle("./data/characters.pickle")
df_text = pd.read_pickle("./data/voice_text.pickle")

# for traveler
df_chars.loc[df_chars["Name"] == "Traveler", "Element"] = "Traveler"

st.title("Network Graph of Genshin Impact Characters")

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


def get_node_options(char):
    colormap = {
        "Pyro": "rgb(205,134,71)",
        "Hydro": "rgb(140,190,235)",
        "Electro": "rgb(167,147,190)",
        "Cryo": "rgb(145,163,176)",
        "Anemo": "rgb(147,184,166)",
        "Geo": "rgb(223,186,81)",
        "Dendro": "rgb(176,198,86)",
    }

    entries = df_chars[df_chars["Name"] == char]
    if len(entries) > 0:
        entry = entries.iloc[0]

        node_options = {
            "size": 250,
            "shape": "circularImage",
            "image": entry["Image"],
            "group": entry["Element"] or "Others",
            "color": colormap.get(entry["Element"], "white"),
        }

        if char not in selected_characters:
            node_options["opacity"] = 0.5
        return node_options
    else:
        return {
            "size": 250,
            "shape": "circularImage",
            "image": f"https://ui-avatars.com/api/?rounded=true&bold=true&size=512&format=png&name={char}",
        }


def add_fullscreen(filepath):
    with open(filepath) as f:
        soup = BeautifulSoup(f, "lxml")

    script_soup = BeautifulSoup(
        """\
<script>
document.onkeydown = function(e){
    e = e || window.event;
    var key = e.which || e.keyCode;
    if(key===70){
        if(!document.fullscreenElement){
            var networkEl = document.getElementById("mynetwork").requestFullscreen();
            if(networkEl.requestFullScreen) {
                networkEl.requestFullScreen();
            } else if (networkEl.webkitRequestFullScreen) {
                networkEl.webkitRequestFullScreen();
            } else if (networkEl.mozRequestFullScreen) {
                networkEl.mozRequestFullScreen();
            }
        } else {
            document.exitFullscreen();
        }
    }
};
</script>
""",
        "lxml",
    )

    soup.body.append(script_soup.html.head.script)

    with open(filepath, "w") as f:
        f.write(str(soup))


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

        gs_net.add_node(src, src, title=src, **get_node_options(src))
        gs_net.add_node(dst, dst, title=dst, **get_node_options(dst))
        gs_net.add_edge(src, dst, value=w)

    gs_net.toggle_physics(True)

    if platform.processor():  # local
        path = "./public"
        if not os.path.exists(path):
            os.mkdir(path)
    else:  # cloud
        path = "/tmp"

    gs_net.set_options(
        """\
{
    "configure": {
        "enabled": false
    },
    "edges": {
        "arrowStrikethrough": false,
        "color": {
            "inherit": true
        },
        "smooth": {
            "enabled": true,
            "type": "dynamic"
        }
    },
    "interaction": {
        "dragNodes": true,
        "hideEdgesOnDrag": false,
        "hideNodesOnDrag": false
    },
    "physics": {
        "barnesHut": {
            "avoidOverlap": 0,
            "centralGravity": 0.3,
            "damping": 0.09,
            "gravitationalConstant": -80000,
            "springConstant": 0.001,
            "springLength": 250
        },
        "enabled": true,
        "stabilization": {
            "enabled": true,
            "fit": true,
            "iterations": 1000,
            "onlyDynamicEdges": false,
            "updateInterval": 50
        }
    }
}
"""
    )

    gs_net.show(f"{path}/genshin_network.html")
    add_fullscreen(f"{path}/genshin_network.html")
    html_file = open(f"{path}/genshin_network.html", "r", encoding="utf-8")

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
