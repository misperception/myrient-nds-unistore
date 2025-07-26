import zipfile

import os, requests
from zipfile import ZipFile
from tools.bannergif import bannergif
from modules.databases import get_crc

class T3S:
    path: str
    filename: str
    max_entries: int
    index: int
    region: str

    def __init__(self, region, index, max_entries):
        self.max_entries = max_entries
        self.index = index // self.max_entries
        self.region = region.lower()
        self.filename = f"myrient-nds-{self.region}-{self.index}.t3s"
        self.path = f"icons/{region}/{self.filename}"

        if os.path.exists(self.path): return
        with open(self.path, "x+") as file:
            file.write("--atlas -f rgba -z auto\n\n")
        self.generate_t3x_script()

    def append(self, name):
        with open(self.path, "a+") as file:
            file.write(f"\"{name}\"\n")

    def generate_t3x_script(self):
        if not os.path.exists("generate_t3x.sh"):
            with open("generate_t3x.sh", "w") as file: file.write("#! /bin/bash\n\n")
            os.makedirs("unistore/icons", exist_ok=True)
        with open("generate_t3x.sh", "a") as file:
            file.write(f"tex3ds -i {self.path} -o \"unistore/icons/{self.filename.replace(".t3s", ".t3x")}\" > /dev/null\n")

class Icon:
    icon_index: int
    path: str
    filename: str
    t3s: T3S

    def __init__(self, path, filename, index):
        self.icon_index = index % 512
        self.path = path + filename
        self.filename = filename
        os.makedirs(path, exist_ok=True)

    @classmethod
    def get_icon(cls, title: str, region: str, index: int, databases: dict):
        icon = cls(f"icons/{region}/", f"{title}.png", index)
        icon.t3s = T3S(region, index, 512)
        print(f"Fetching icon for {title}...")

        if os.path.exists(icon.path):
            print(f"Icon exists, skipping")
            icon.t3s.append(icon.filename)
            return icon

        crc = get_crc(title, databases)
        try:
            id = image_id_from_crc(crc, databases)
            url = url_from_image_id(id)
            data = requests.get(url).content
            with open(icon.path, "wb") as file:
                file.write(data)
        except Exception:
            print("Title not found in ADVANsCEne database, getting icon from ROM...")
            fallback_icon(title, region)

        icon.t3s.append(icon.filename)
        return icon

def download_rom(title: str):
    os.makedirs("temp", exist_ok=True)
    data = requests.get(f"https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Encrypted%29/{title+".zip"}")
    # Download and extract zip file
    with open("temp/temp.zip", "w+b") as zip:
        zip.write(data.content)
        try: name = ZipFile(zip).extract(member=f"{title+".nds"}", path="temp")
        except zipfile.BadZipfile:
            print("Retrying...")
            download_rom(title)
            return
    # Rename nds file and delete zip file
    os.remove("temp/temp.zip")
    os.rename(name, "temp/temp.nds")

def fallback_icon(title: str, region: str):
    path = f"icons/{region}/{title}.png"
    download_rom(title)
    with open("temp/temp.nds", "rb") as rom:
        bannergif(rom, path)

def image_id_from_crc(crc: str, databases: dict) -> str:
    propers = databases["propers"]
    advanscene = databases["advanscene"]
    # Scan the "propers" database in search for releases (should be most entries)
    for game in propers:
        game_crc = game.find("rom").attrib["crc"]
        if game_crc == crc:
            game_id = game.attrib["name"][:4]

    for game in advanscene:
        # If found in propers, extract the image id from the scene id
        if game_id and game.findtext("comment") == game_id:
            id = game.findtext("imageNumber")
            return id
        # Otherwise, attempt to find the CRC for the game and extract image id
        game_crc = game.find("files").findtext("romCRC")
        if game_crc.lower() == crc.lower():
            id = game.findtext("imageNumber")
            return id
    # If the code reaches this point, the game is most definitely not in the database
    raise Exception("Title not found")

def url_from_image_id(id: str) -> str:
    id = int(id)
    start, end = (0, 0)
    while end < id:
        start=end
        end+=500
    url = f"https://www.advanscene.com/offline/imgs/NDSicon/{start+1}-{end}/{id:04}.png"
    return url