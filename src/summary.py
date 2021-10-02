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

    app = applications["Code.exe"]
    app.save_to_json("code_exe.json")
    des = Application.load_from_json("code_exe.json")
    print(app == des)
    des2 = Application.load_from_json("old_code_exe.json")
    print(app == des2)

    KEYS = ["nane", "pids", "exe", "startup", "shutdown", "uniqueid"]

    DEBUG_DB = True
    daystamp = get_daystamp()
    db_path = Path("apps-on-%s.db" % daystamp.strftime(DATE_FORMAT))

    if DEBUG_DB:
        db_path.unlink(missing_ok=True)

    con = sqlite3.connect(db_path)

    TABLE_NAME = "Applications"
    columns = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        + " TEXT, ".join(KEYS)
        + " TEXT"
    )
    unique_keys = ["place_id TEXT"]
    for uk in unique_keys:
        columns = columns.replace(uk, "%s UNIQUE" % uk)

    con.cursor().execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({columns})"""
    )

    # def add_data_to_db(data):
    #     values_template = "NULL, " + \
    #         ", ".join(["?" for _ in range(len(KEYS))])
    #     # table_data = [tuple(get_important_data(d).values()) for d in data]
    #     con.cursor().executemany(
    #         f"""insert or ignore into {TABLE_NAME} \
    #             values ({values_template})""",
    #         # table_data,
    #     )
    #     con.commit()

    # def select_all_data_from_db():
    #     return con.cursor().execute(f"""select * from {TABLE_NAME}""")
