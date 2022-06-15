import os
import platform

from bs4 import BeautifulSoup


def get_html_path():
    if platform.processor():  # local
        path = "./public"
        if not os.path.exists(path):
            os.mkdir(path)
    else:  # cloud
        path = "/tmp"

    return path


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
        
def get_node_options(char, df_chars, size=250, selected_characters=None):
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

        if selected_characters and char not in selected_characters:
            node_options["opacity"] = 0.5
        return node_options
    else:
        return {
            "size": 250,
            "shape": "circularImage",
            "image": f"https://ui-avatars.com/api/?rounded=true&bold=true&size=512&format=png&name={char}",
        }

def get_node_options_dish(char, df_chars, size=250):
    entries = df_chars[df_chars["name"] == char]
    if len(entries) > 0:
        entry = entries.iloc[0]

        node_options = {
            "size": 250,
            "shape": "circularImage",
            "image": entry["image"]
        }

        return node_options
    else:
        return {
            "size": 250,
            "shape": "circularImage",
            "image": f"https://ui-avatars.com/api/?rounded=true&bold=true&size=512&format=png&name={char}",
        }

def remove_duplicates(df):
    df['Combination'] = df[['Source', 'Target']].apply(lambda x: '-'.join(sorted(x.tolist())), axis=1)
    df = df.drop_duplicates(subset='Combination')
    df = df.drop(columns=['Combination'])
    df = df.reset_index(drop=True)
    return df