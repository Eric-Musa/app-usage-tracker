from pathlib import Path
import sqlite3
from .scheduling import DATE_FORMAT
from .summary import create_table, get_db_path

ARCHIVE_LOG_PATH = Path.cwd().parent / "data" / "archive_log.db"
ARCHIVE_LOG_TABLE = "ArchiveLog"


def archive_db(db_path, daystamp, response, archive_log_path=ARCHIVE_LOG_PATH):
    archive_db_path = db_path.rename(
        str(db_path).replace(".db", "_archive.db")
    )

    con = sqlite3.connect(archive_log_path)

    arc_columns = [
        "daystamp",
        "archived_db_path",
        "notif_errors",
    ]
    unique_arc_columns = ["daystamp TEXT"]
    create_table(con, ARCHIVE_LOG_TABLE, arc_columns, unique_arc_columns)

    values_template = "NULL, " + ", ".join(
        ["?" for _ in range(len(arc_columns))]
    )
    con.cursor().execute(
        f"""
        insert or ignore into {ARCHIVE_LOG_TABLE} values ({values_template})
        """,
        (daystamp, archive_db_path.name, str(response)),
    )
    con.commit()
    return archive_db_path


def exists_and_is_archived(
    daystamp, db_path=None, archive_log_path=ARCHIVE_LOG_PATH
):
    con = sqlite3.connect(archive_log_path)
    daystamp_matches = (
        con.cursor()
        .execute(
            f'''select daystamp from {ARCHIVE_LOG_TABLE}
                where daystamp == "{daystamp.strftime(DATE_FORMAT)}"'''
        )
        .fetchall()
    )
    if len(daystamp_matches) == 1:
        return True, True  # exists and is archived
    else:
        db_path = db_path or get_db_path(daystamp)
        if db_path.exists():
            return True, False  # exists but was not archived
        else:
            return False, False  # neither exists nor was archived
