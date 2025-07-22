import os, json
from urllib.parse import quote
from modules.misc import sanitize

def create_store(region: str, index: int):
    print("Creating UniStore files...")
    os.makedirs("unistore", exist_ok=True)
    store = {
        "storeInfo": {
            "title": f"Myrient DS Store {region}",
            "author": "misper_ception",
            "description": "A UniStore for downloading NDS games through Myrient",
            "file": f"myrient-nds-{region.lower()}.unistore",
            "url": f"https://raw.githubusercontent.com/misperception/myrient-nds-unistore/master/unistore/myrient-nds-{region.lower()}.unistore",
            "sheet": [f"myrient-nds-{region.lower()}-{i}.t3x" for i in range(index//512 + 1)],
            "sheetURL": [f"https://raw.githubusercontent.com/misperception/myrient-nds-unistore/master/unistore/icons/myrient-nds-{region.lower()}-{i}.t3x"
                         for i in range(index//512 + 1)],
            "version": 3,
            "revision": 3
        },
        "storeContent": []
    }

    with open(f"unistore/myrient-nds-{region.lower()}.unistore", "w") as file:
        json.dump(store, file, indent=4)

def generate_entry(title: str, index: int) -> dict:
    print(f"Generating entry index {index}...")
    entry = {
        "info": {
            "title": sanitize(title),
            # "author": "$author",
            # "description": "$description",
            # "category": ["a"],
            "console": ["DS"],
            "icon_index": index%512,
            "sheet_index": index//512,
            # "last_updated": "$release",
            # "version": "$version"
        },
        title: [
            {
                "type": "downloadFile",
                "file": f"https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Encrypted%29/{quote(title)}",
                "output": f"%ARCHIVE_DEFAULT%/{title}"
            },
            {
                "type": "extractFile",
                "file": f"%ARCHIVE_DEFAULT%/{title}",
                "input": ".*",
                "output": f"%NDS%/{title.replace(".zip", ".nds")}"
            },
            {
                "type": "deleteFile",
                "file": f"%ARCHIVE_DEFAULT%/{title}"
            }
        ]
    }
    return entry

def append_entries(entries: dict):
    for region, list in entries.items():
        with open(f"unistore/myrient-nds-{region.lower()}.unistore", "r+") as file:
            data = json.load(file)
        data.update({"storeContent": list})
        with open(f"unistore/myrient-nds-{region.lower()}.unistore", "w") as file:
            json.dump(data, file, indent=4)