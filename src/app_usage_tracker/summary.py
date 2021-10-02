import psutil
import sqlite3
from pathlib import Path
from application import Application
from categories import (
    categorize,
    OTHER,
)
from scheduling import (
    get_daystamp,
    DATE_FORMAT,
)

# from app_usage_tracker.application import bad_hash


def create_table(db_con, table_name, columns, unique_columns):
    columns = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        + " TEXT, ".join(columns)
        + " TEXT"
    )
    for uc in unique_columns:
        columns = columns.replace(uc, "%s UNIQUE" % uc)

    db_con.cursor().execute(
        f"""CREATE TABLE IF NOT EXISTS {table_name} ({columns})"""
    )


def scrape(exclude_other=True):

    # SCRAPE
    applications = {}
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

    # CONNECT TO DB
    daystamp = get_daystamp()
    db_path = (
        Path.cwd().parent.parent
        / "data"
        / ("apps-on-%s.db" % daystamp.strftime(DATE_FORMAT))
    )

    con = sqlite3.connect(db_path)

    # DEFINE COLUMN NAMES
    name = "name"
    category = "category"
    startup = "startup"
    shutdown = "shutdown"
    pids = "pids"
    exe = "exe"
    uid = "uid"
    walltime = "walltime"

    # UPDATE APPLICATION DATA
    application_table = "Applications"
    app_columns = [
        name,
        category,
        startup,
        shutdown,
        pids,
        exe,
        uid,
    ]
    unique_app_columns = ["uid TEXT"]
    create_table(con, application_table, app_columns, unique_app_columns)

    values_template = "NULL, " + ", ".join(
        ["?" for _ in range(len(app_columns))]
    )
    con.cursor().executemany(
        f"""
        insert or replace into {application_table} values ({values_template})
        """,
        list(app.as_db_record() for app in applications.values()),
    )
    con.commit()

    # UPDATE AGGREGATIONS TABLE
    aggregation_table = "Aggregations"
    agg_columns = [name, category, walltime]
    unique_agg_columns = [f"{name} TEXT"]
    create_table(con, aggregation_table, agg_columns, unique_agg_columns)

    # perform aggregation
    con.cursor().execute(
        f"""
        insert or replace into {aggregation_table}
        ({name}, {category}, {walltime})
        select
        {name}, {category}, time(
            sum(
                (strftime('%s', {shutdown}) - strftime('%s', {startup}))
            ), 'unixepoch') as "{walltime}"
        from {application_table}
        group by {name}
        order by {walltime} desc
        """
    )
    con.commit()
