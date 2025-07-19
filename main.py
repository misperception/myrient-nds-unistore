import requests
from modules.databases import init_databases
from modules.icons import get_icon
from modules.entries import generate_entry, append_entries, create_store
from modules.misc import get_region
from bs4 import BeautifulSoup

def crawl():
    print("Initiating crawl...")
    FORBIDDEN_TAGS = ("[bios]", "(demo)", "(beta", "(proto", "(kiosk)", "(save data)", "[b]", "(program)", "(unl)", "(wii u virtual console)")
    entries = {
        "Europe": [],
        "USA": [],
        "Japan": [],
        "Misc": []
    }
    indexes = {
        "Europe": 0,
        "USA": 0,
        "Japan": 0,
        "Misc": 0
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
            if tag in link.text.lower():
                forbidden = True
        if forbidden: continue

        entry_name = link.text.strip()
        print(entry_name)
        region = get_region(entry_name)
        get_icon(entry_name, region, indexes[region], databases)
        entry = generate_entry(entry_name, indexes[region])
        entries[region].append(entry)
        indexes[region]+=1

    return entries, indexes

if __name__ == "__main__":
    entries, regions = crawl()
    for region, index in regions.items(): create_store(region, index)
    append_entries(entries)