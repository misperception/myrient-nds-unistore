from xml.etree import ElementTree

def init_advanscene():
    database = ElementTree.parse("databases/advanscene.xml")
    root = database.getroot()
    games = root.find("games")
    return games

def init_nointro():
    database = ElementTree.parse("databases/no-intro.xml")
    games = database.getroot()
    games.remove(games.find("header"))
    return games

def init_propers():
    propers = ElementTree.parse("databases/propers.xml")
    games = propers.getroot()
    games.remove(games.find("header"))
    return games

def init_databases():
    databases = {
        "advanscene": init_advanscene(),
        "no-intro": init_nointro(),
        "propers": init_propers()
    }
    return databases

def get_crc(title: str, databases: dict) -> str:
    no_intro = databases["no-intro"]
    for game in no_intro:
        if game.attrib["name"] == title.removesuffix(".zip"):
            rom = game.find("rom")
            crc = rom.attrib["crc"]
            return crc