import os, json, subprocess
from shutil import which
from urllib.parse import quote
from modules.misc import sanitize, get_region
from modules.icons import Icon

class Entry:
    region: str
    index: int
    title: str
    filename: str
    url: str
    _entry: dict
    _icon: Icon
    _databases: dict

    def __init__(self, title: str, stores, databases):
        self.filename = title
        self.title = sanitize(title)
        self.region = get_region(title)
        self.store = stores[self.region]
        self.index = self.store.length
        self.url = f"https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Encrypted%29/{quote(title)}"
        self._databases = databases

    @property
    def entry(self):
        try: return self._entry
        except AttributeError:
            self._entry = {
                "info": {
                    "title": self.title,
                    # "author": "$author",
                    # "description": "$description",
                    # "category": ["a"],
                    "console": ["DS"],
                    "icon_index": self.icon.icon_index,
                    "sheet_index": self.icon.t3s.index,
                    # "last_updated": "$release",
                    # "version": "$version"
                },
                self.filename: [
                    {
                        "type": "downloadFile",
                        "file": self.url,
                        "output": f"%ARCHIVE_DEFAULT%/{self.filename}"
                    },
                    {
                        "type": "extractFile",
                        "file": f"%ARCHIVE_DEFAULT%/{self.filename}",
                        "input": ".*",
                        "output": f"%NDS%/{self.filename.replace(".zip", ".nds")}"
                    },
                    {
                        "type": "deleteFile",
                        "file": f"%ARCHIVE_DEFAULT%/{self.filename}"
                    }
                ]
            }
            return self._entry

    @property
    def icon(self):
        try: return self._icon
        except AttributeError:
            self._icon = Icon.get_icon(self.title, self.region, self.index, self._databases)
            return self._icon

    def append_to_store(self):
        self.store.entries.append(self)

class Store:
    region: str
    entries: list[Entry]
    length: int
    max_icons_allowed: int
    path: str
    sheets: list[str]

    def __init__(self, region, max_icons):
        self.region = region
        self.entries = []
        self.max_icons_allowed = max_icons
        self.path = f"unistore/myrient-nds-{self.region.lower()}.unistore"

    @property
    def length(self):
        return len(self.entries)

    @property
    def sheets(self):
        return [f"myrient-nds-{self.region.lower()}-{i}.t3x" for i in range(self.length//self.max_icons_allowed + 1)]

    @property
    def dict(self):
        store = {
            "storeInfo": {
                "title": f"Myrient DS Store {self.region}",
                "author": "misper_ception",
                "description": "A UniStore for downloading NDS games through Myrient",
                "file": f"myrient-nds-{self.region.lower()}.unistore",
                "url": f"https://raw.githubusercontent.com/misperception/myrient-nds-unistore/master/{self.path}",
                "sheet": self.sheets,
                "sheetURL": [f"https://raw.githubusercontent.com/misperception/myrient-nds-unistore/master/unistore/icons/{sheet}"
                             for sheet in self.sheets],
                "version": 3,
                "revision": 4
            },
            "storeContent": [entry.entry for entry in self.entries]
        }
        return store

    @property
    def t3s(self):
        return {entry.icon.t3s for entry in self.entries}

    def create_unistore(self):
        os.makedirs("unistore/icons", exist_ok=True)
        with open(self.path, "w") as file:
            json.dump(self.dict, file, indent=4)
        if not which("tex3ds"):
            print("devkitPro toolchain not detected, skipping t3x creation...")
        print("Compressing icons, this may take a while...")
        for t3s, t3x in zip(self.t3s, self.sheets):
            subprocess.run(["tex3ds", "-i", f"{t3s.path}", "-o", f"unistore/icons/{t3x}"], stdout = subprocess.DEVNULL)
            print(f"{t3x} created.")