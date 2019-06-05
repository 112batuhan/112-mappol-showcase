import requests, json
import urllib.request
from pathlib import Path


class Beatmap:

    def __init__(self, id):
        self.id = id

        folder_dir = Path("backgrounds")
        folder_dir.mkdir(exist_ok=True)

        api = "3c76fadf34e0b07eff6515607793606c83f334fa"
        url = f"https://osu.ppy.sh/api/get_beatmaps?k={api}&b={self.id}"

        r = requests.get(url)
        map_info = json.loads(r.text)[0]

        self.set_id = map_info["beatmapset_id"]
        self.artist = map_info["artist"]
        self.title = map_info["title"]
        self.diff_name = map_info["version"]
        self.mapper = map_info["creator"]

        url = f"https://assets.ppy.sh/beatmaps/{self.set_id}/covers/cover.jpg"
        self.image_path = f"{folder_dir}/{self.id}.jpg"

        if not Path(self.image_path).exists():
            urllib.request.urlretrieve(url, self.image_path)
            print(f"Downloading image {self.id}")


def get_pool():
    maps = {}

    with open('pool.txt') as f:
        content = f.read().splitlines()

    mod = ""
    for line in content:

        if line == "-NM-":
            mod = "No Mod"
        elif line == "-HD-":
            mod = "Hidden"
        elif line == "-HR-":
            mod = "Hard Rock"
        elif line == "-DT-":
            mod = "Double Time"
        elif line == "-FM-":
            mod = "Free Mod"
        elif line == "-TB-":
            mod = "Tie Breaker"
        else:

            try:
                maps[mod].append(line)

            except KeyError:
                maps.update({mod: []})
                maps[mod].append(line)

    return maps
