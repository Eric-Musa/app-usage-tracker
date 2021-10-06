from operator import attrgetter
from pathlib import Path
import psutil
import sqlite3
from .application import Application, STILL_RUNNING
from .categories import (
    categorize,
    OTHER,
)
from .scheduling import (
    get_daystamp_and_cutoff_datetime,
    DATE_FORMAT,
)


def get_db_path(daystamp):
    return (
        Path.cwd().parent
        / "data"
        / ("apps-on-%s.db" % daystamp.strftime(DATE_FORMAT))
    )


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


def scrape(db_path=None, exclude_other=True):

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

    daystamp, _ = get_daystamp_and_cutoff_datetime()

    # CONNECT TO DB
    db_path = db_path or get_db_path(daystamp)
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

    # set all running app statuses to stopped before inserting new values
    con.cursor().execute(
        f"""
        update {application_table}
        set {shutdown} = datetime('now', 'localtime')
        where {shutdown} == '{STILL_RUNNING}'
        """
    )
    con.commit()

    # now insert new values, overwriting previously "stopped" apps
    values_template = "NULL, " + ", ".join(
        ["?" for _ in range(len(app_columns))]
    )
    values = [
        app.as_db_record()
        for app in sorted(
            applications.values(), key=attrgetter("startup"), reverse=True
        )
    ]
    con.cursor().executemany(
        f"""
        insert or replace into {application_table} values ({values_template})
        """,
        values,
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
                (strftime('%s', (case when {shutdown} == '{STILL_RUNNING}'
                    then datetime('now', 'localtime') else {shutdown} end))
                        - strftime('%s', {startup}))
            ), 'unixepoch'
        ) as "{walltime}"
        from {application_table}
        group by {name}
        order by {walltime} desc
        """
    )
    con.commit()

    return (
        db_path,
        con.cursor()
        .execute(
            f"""select {name}, {category}, {walltime}
                from {aggregation_table}"""
        )
        .fetchall(),
    )


if __name__ == "__main__":

    daystamp, _ = get_daystamp_and_cutoff_datetime()

    debug = False
    if debug:
        db_path = (
            Path.cwd().parent.parent
            / "data"
            / ("apps-on-%s_debug2.db" % daystamp.strftime(DATE_FORMAT))
        )
        clean_db = False
        if clean_db:
            print("deleting", db_path)
            db_path.unlink(missing_ok=True)

    print("scraping")
    scrape(db_path)
    print("scraped")
