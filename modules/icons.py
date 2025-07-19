import os, requests, re
from zipfile import ZipFile
from tools.bannergif import bannergif
from modules.misc import sanitize
from shutil import copy
from modules.databases import get_crc

def generate_t3x_script(path: str, filename: str):
    if not os.path.exists("generate_t3x.sh"):
        with open("generate_t3x.sh", "w") as file: file.write("#! /bin/bash\n\n")
        os.makedirs("unistore/icons", exist_ok=True)
    with open("generate_t3x.sh", "a") as file:
        file.write(f"tex3ds -i {f"{path}/{filename}"} -o \"unistore/icons/{filename.replace(".t3s", ".t3x")}\" > /dev/null\n")

def make_t3s(region: str, tex_index: int):
    path = f"icons/{region}"
    filename = f"myrient-nds-{region.lower()}-{tex_index}.t3s"
    os.makedirs(path, exist_ok=True)
    if os.path.exists(f"{path}/{filename}"): return
    with open(f"{path}/{filename}", "x+") as file:
        file.write("--atlas -f rgba -z auto\n\n")
    generate_t3x_script(path, filename)

def append_to_t3s(region: str, title: str, tex_index: int = 0):
    title = sanitize(title)
    with open(f"icons/{region}/myrient-nds-{region.lower()}-{tex_index}.t3s", "a") as file:
        file.write(f"\"{title}.png\"\n")

def get_icon(title: str, region: str, index: int, databases: dict):
    title = sanitize(title)
    path = f"icons/{region}/{title}.png"
    make_t3s(region, index//512)
    print(f"Fetching icon for {region} entry index {index}...")
    if os.path.exists(path):
        print(f"Icon exists, skipping")
        append_to_t3s(region, title, index//512)
        return
    alt_path = re.sub(r"\(Rev .\)", "", path).strip()
    if os.path.exists(alt_path):
        print(f"Reusable icon exists, copying")
        copy(alt_path, path)
        append_to_t3s(region, title, index//512)
        return
    crc = get_crc(title, databases)
    try:
        id = image_id_from_crc(crc, databases)
        url = url_from_image_id(id)
        image = requests.get(url).content
        with open(path, "wb") as icon:
            icon.write(image)
    except Exception:
        print("Title not found in ADVANsCEne database, getting icon from ROM...")
        fallback_icon(title, region)
    append_to_t3s(region, title, index//512)

def download_rom(title: str):
    os.makedirs("temp", exist_ok=True)
    data = requests.get(f"https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Encrypted%29/{title+".zip"}")
    # Download and extract zip file
    with open("temp/temp.zip", "w+b") as zip:
        zip.write(data.content)
        name = ZipFile(zip).extract(member=f"{title+".nds"}", path="temp")
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