def sanitize(title: str) -> str:
    title = title.strip()
    title = title.removesuffix(".zip")
    return title.strip()

def get_region(title: str) -> str:
    if "(europe)" in title.lower(): return "Europe"
    if "(usa)" in title.lower(): return "USA"
    if "(japan)" in title.lower(): return "Japan"
    return "Misc"