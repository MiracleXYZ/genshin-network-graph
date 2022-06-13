import platform

import pandas as pd
from prompt_toolkit import PromptSession
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

df_chars = pd.read_pickle('./data/characters.pickle')
df_text = pd.read_pickle('./data/voice_text.pickle')

st.title('Network Graph of Genshin Impact Characters')

def get_node_options(char):
    colormap = {
        'Pyro': 'rgb(205,134,71)',
        'Hydro': 'rgb(140,190,235)',
        'Electro': 'rgb(167,147,190)',
        'Cryo': 'rgb(145,163,176)',
        'Anemo': 'rgb(147,184,166)',
        'Geo': 'rgb(223,186,81)',
        'Dendro': 'rgb(176,198,86)',
    }

    entries = df_chars[df_chars['Name'] == char]
    if len(entries) > 0:
        entry = entries.iloc[0]

        return {
            'size': 250,
            'shape': 'circularImage',
            'image': entry['Image'],
            'group': entry['Element'] or 'Others',
            'color': colormap.get(entry['Element'], 'white'),
        }
    else:
        return {
            'size': 250,
            'shape': 'circularImage',
            'image': f'https://ui-avatars.com/api/?rounded=true&bold=true&size=512&format=png&name={char}'
        }

elements = df_chars['Element'].drop_duplicates().tolist()
regions = df_chars['Region'].drop_duplicates().tolist()

selected_elements = st.multiselect('Select Element(s)', elements, default=elements)
selected_regions = st.multiselect('Select Region(s)', regions, default=regions)
selected_characters = df_chars[
    (df_chars['Element'].isin(selected_elements)) & (df_chars['Region'].isin(selected_regions))
]['Name'].tolist()

df_text = df_text[df_text['Source'].isin(selected_characters)]

if len(df_text) == 0:
    st.write('No data found. Select elements and regions to start with.')
else:

    gs_net = Network(
        height='600px',
        width='100%',
        directed=True
    )

    gs_net.barnes_hut()

    for idx, row in df_text.iterrows():
        src = row['Source']
        dst = row['Target']
        w = row['Sentiment']

        if src == dst:
            continue

        gs_net.add_node(
            src, src, title=src,
            **get_node_options(src)
        )
        gs_net.add_node(
            dst, dst, title=dst,
            **get_node_options(dst)
        )
        gs_net.add_edge(src, dst, value=w)

    gs_net.toggle_physics(True)


    if platform.processor(): # local
        path = './public'
    else:
        path = '/tmp'

    gs_net.show(f'{path}/genshin_network.html')
    html_file = open(f'{path}/genshin_network.html', 'r', encoding='utf-8')

    components.html(html_file.read(), height=600)
