from pathlib import Path

def classify(exe_path):
    exe_path = Path(exe_path)
    categories = {
        'work': WORK,
        'leisure': LEISURE,
        'browser': BROWSER,
    }
    for category, cat_list in categories.items():
        if exe_path.name in cat_list or any(part in cat_list for part in exe_path.parts):
            return category
    return 'other'


WORK = [
    'Microsoft Office',
    'Code.exe',
    'zotero.exe',
    'DB Browser for SQLite.exe',
    'tableau.exe',
]

LEISURE = [
    'SteamLibrary',
    'Ubisoft Games'
]

BROWSER = [
    'chrome.exe',
]