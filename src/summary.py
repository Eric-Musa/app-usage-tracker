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

    # SCRAPE
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

    # TEST
    # app = applications["Code.exe"]
    # app.save_to_json("code_exe.json")
    # des = Application.load_from_json("code_exe.json")
    # print(app == des)
    # des2 = Application.load_from_json("old_code_exe.json")
    # print(app == des2)

    # CONNECT TO DB
    daystamp = get_daystamp()
    db_path = Path("apps-on-%s_2.db" % daystamp.strftime(DATE_FORMAT))

    DEBUG_DB = False
    if DEBUG_DB:
        db_path.unlink(missing_ok=True)

    con = sqlite3.connect(db_path)

    # UPDATE APPLICATION DATA
    application_table = "Applications"
    application_keys = [
        "name",
        "category",
        "startup",
        "shutdown",
        "pids",
        "exe",
        "uid",
    ]
    app_columns = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        + " TEXT, ".join(application_keys)
        + " TEXT"
    )
    unique_app_keys = ["uid TEXT"]
    for uk in unique_app_keys:
        app_columns = app_columns.replace(uk, "%s UNIQUE" % uk)

    con.cursor().execute(
        f"""CREATE TABLE IF NOT EXISTS {application_table} ({app_columns})"""
    )

    values_template = "NULL, " + ", ".join(
        ["?" for _ in range(len(application_keys))]
    )
    con.cursor().executemany(
        f"""insert or replace into {application_table} \
            values ({values_template})""",
        list(app.as_db_record() for app in applications.values()),
    )
    con.commit()

    # UPDATE AGGREGATIONS TABLE
    aggregation_table = "Aggregations"
    aggregation_keys = ["name", "category", "walltime"]
    agg_columns = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        + " TEXT, ".join(aggregation_keys)
        + " TEXT"
    )
    unique_agg_keys = ["name TEXT"]
    for uk in unique_agg_keys:
        agg_columns = agg_columns.replace(uk, "%s UNIQUE" % uk)

    con.cursor().execute(
        f"""CREATE TABLE IF NOT EXISTS {aggregation_table} ({agg_columns})"""
    )

    # perform aggregation
    values_template = "NULL, " + ", ".join(
        ["?" for _ in range(len(aggregation_keys))]
    )
    con.cursor().execute(
        f"""
    insert or replace into {aggregation_table} (name, category, walltime)
    select
    name, category, time(
        sum(
            (strftime('%s', shutdown) - strftime('%s', startup))
        ), 'unixepoch') as "walltime"
    from {application_table}
    group by name
    order by walltime desc
    """
    )
    con.commit()

    # UPDATE SUMMARY TABLE
    summary_table = "Summary"
    summary_keys = ["category", "'total walltime'"]
    sum_columns = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        + " TEXT, ".join(summary_keys)
        + " TEXT"
    )
    unique_sum_keys = ["category TEXT"]
    for uk in unique_sum_keys:
        sum_columns = sum_columns.replace(uk, "%s UNIQUE" % uk)

    con.cursor().execute(
        f"""CREATE TABLE IF NOT EXISTS {summary_table} ({sum_columns})"""
    )

    # perform summary
    values_template = "NULL, " + ", ".join(
        ["?" for _ in range(len(summary_keys))]
    )
    con.cursor().execute(
        f"""
    insert or replace into {summary_table} (category, "total walltime")
    select
    category, time(
        sum(
            strftime('%s', walltime)
            ), 'unixepoch') as "total walltime"
    from {aggregation_table}
    group by category
    order by walltime desc
    """
    )
    con.commit()
