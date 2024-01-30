import os
import platform
import json

from bs4 import BeautifulSoup

with open("./data/input/colormap.json", "r") as f:
    COLORMAP = json.load(f)

with open("./data/input/addmap.json", "r") as f:
    ADDMAP = json.load(f)


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
var toggleFullScreen = function(el) {
    if(!document.fullscreenElement){
        if(el.requestFullScreen) {
            el.requestFullScreen();
        } else if (el.webkitRequestFullScreen) {
            el.webkitRequestFullScreen();
        } else if (el.mozRequestFullScreen) {
            el.mozRequestFullScreen();
        }
    } else {
        document.exitFullscreen();
    }
}

var networkEl = document.getElementById("mynetwork");
document.onkeydown = function(e){
    e = e || window.event;
    var key = e.which || e.keyCode;
    if(key===70){
        toggleFullScreen(networkEl);
    }
};
networkEl.addEventListener("dblclick", function() {
    toggleFullScreen(networkEl);
});
</script>
""",
        "lxml",
    )

    soup.body.append(script_soup.html.head.script)

    with open(filepath, "w") as f:
        f.write(str(soup))


def get_node_options(char, df_chars, size=250, selected_characters=None):
    entries = df_chars[df_chars["Name"] == char]
    if len(entries) > 0:
        entry = entries.iloc[0]

        node_options = {
            "size": 250,
            "shape": "circularImage",
            "image": entry["Image"],
            "group": entry["Element"] or "Others",
            "color": COLORMAP.get(entry["Element"], "white"),
        }

        if selected_characters and char not in selected_characters:
            node_options["opacity"] = 0.5
        return node_options
    else:
        return {
            "size":
            250,
            "shape":
            "circularImage",
            "image":
            ADDMAP.get(
                char,
                f"https://ui-avatars.com/api/?rounded=true&bold=true&size=512&format=png&name={char}"
            ),
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
            "size":
            250,
            "shape":
            "circularImage",
            "image":
            f"https://ui-avatars.com/api/?rounded=true&bold=true&size=512&format=png&name={char}",
        }


def remove_duplicates(df):
    df["Combination"] = df[["Source", "Target"
                            ]].apply(lambda x: "-".join(sorted(x.tolist())),
                                     axis=1)
    df = df.drop_duplicates(subset="Combination")
    df = df.drop(columns=["Combination"])
    df = df.reset_index(drop=True)
    return df
