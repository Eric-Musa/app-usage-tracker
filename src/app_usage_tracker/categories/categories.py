from pathlib import Path
import json


WORK = "WORK"
LEISURE = "LEISURE"
COMMON = "COMMON"
OTHER = "OTHER"

categorized_processes_path = (
    Path(__file__).parent / "categorized_processes.json"
)
print(categorized_processes_path.absolute())

with open(categorized_processes_path, "r") as f:
    categorized_processes = json.load(f)
    WORK_APPS = categorized_processes[WORK]
    LEISURE_APPS = categorized_processes[LEISURE]
    COMMON_APPS = categorized_processes[COMMON]


def categorize(exe_path):
    exe_path = Path(exe_path)
    categories = {
        WORK: WORK_APPS,
        LEISURE: LEISURE_APPS,
        COMMON: COMMON_APPS,
    }
    for category, cat_list in categories.items():
        if exe_path.name in cat_list or any(
            part in cat_list for part in exe_path.parts
        ):
            return category
    return OTHER


def add_pattern_to_categorized(key, pattern):
    assert key in [
        WORK,
        LEISURE,
        COMMON,
    ], f"{key} must be in [{WORK}, {LEISURE}, {COMMON}]"
    categorized_processes[key].append(pattern)
    with open(categorized_processes_path, "w") as f:
        json.dump(categorized_processes, f)
