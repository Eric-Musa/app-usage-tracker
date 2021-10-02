import psutil
import sqlite3
from pathlib import Path
from app_usage_tracker import (
    Application,
    categorize,
    OTHER,
    get_daystamp,
    DATE_FORMAT,
)

# from app_usage_tracker.application import bad_hash


if __name__ == "__main__":

    applications = {}
    exclude_other = True

    for proc in psutil.process_iter():
        try:
            name = proc.name()
            if categorize(proc.exe()) == OTHER and exclude_other:
                continue
            if name not in applications:
                applications[name] = Application.from_process(proc)
            else:
                applications[name].add(proc)
        except psutil.AccessDenied as e:
            print(e)

    # app = applications["Code.exe"]
    # app.save_to_json("code_exe.json")
    # des = Application.load_from_json("code_exe.json")
    # print(app == des)
    # des2 = Application.load_from_json("old_code_exe.json")
    # print(app == des2)

    KEYS = ["name", "pids", "exe", "startup", "shutdown", "uid"]

    daystamp = get_daystamp()
    db_path = Path("apps-on-%s.db" % daystamp.strftime(DATE_FORMAT))

    DEBUG_DB = False
    if DEBUG_DB:
        db_path.unlink(missing_ok=True)

    con = sqlite3.connect(db_path)

    TABLE_NAME = "Applications"
    columns = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        + " TEXT, ".join(KEYS)
        + " TEXT"
    )
    unique_keys = ["uid TEXT"]
    for uk in unique_keys:
        columns = columns.replace(uk, "%s UNIQUE" % uk)

    con.cursor().execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({columns})"""
    )

    values_template = "NULL, " + ", ".join(["?" for _ in range(len(KEYS))])
    con.cursor().executemany(
        f"""insert or replace into {TABLE_NAME} \
            values ({values_template})""",
        list(app.as_db_record() for app in applications.values()),
    )
    con.commit()
