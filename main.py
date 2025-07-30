import requests
from modules.databases import init_databases
from modules.entries import Entry, Store
from bs4 import BeautifulSoup

def crawl() -> dict[str, Store]:
    max_icons = 512
    print("Initiating crawl...")
    FORBIDDEN_TAGS = ("[bios]", "(demo)", "(beta", "(proto", "(kiosk)", "(save data)", "[b]", "(program)", "(unl)", "(wii u virtual console)")
    stores = {
        "Europe": Store("Europe", max_icons),
        "USA": Store("USA", max_icons),
        "Japan": Store("Japan", max_icons),
        "Misc": Store("Misc", max_icons),
    }
    page = requests.get("https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20DS%20%28Encrypted%29/")
    crawler = BeautifulSoup(page.text, "html.parser")

    # Initiate databases
    databases = init_databases()

    for item in crawler.find_all("tr"):
        forbidden = False
        link = item.find("a", href=True)
        if not link or "file name" in link.text.lower() or "parent directory" in link.text.lower():
            forbidden = True
        for tag in FORBIDDEN_TAGS:
            if tag in link.text.lower(): forbidden = True
        if forbidden: continue

        entry_name = link.text.strip()
        entry = Entry(entry_name, stores, databases)
        entry.append_to_store()

    return stores

if __name__ == "__main__":
    stores = crawl()
    for store in stores.values(): store.create_unistore()