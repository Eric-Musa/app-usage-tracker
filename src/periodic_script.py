import sqlite3
from app_usage_tracker.scheduling import DAYSTAMP_HOUR_CUTOFF, SCRAPE_INTERVAL
from app_usage_tracker.summary import get_db_path


FROM_EMAIL = "eric.musa.app.usage.tracker@gmail.com"
TO_EMAIL = "eric.musa17@gmail.com"


if __name__ == "__main__":
    import datetime
    import os
    from app_usage_tracker import (
        scrape,
        get_daystamp_and_cutoff_datetime,
        send_summary_email,
        archive_db,
        ARCHIVE_LOG_PATH,
        exists_and_is_archived,
    )

    cutoff_hour = DAYSTAMP_HOUR_CUTOFF
    interval_minutes = SCRAPE_INTERVAL
    from_email = FROM_EMAIL
    to_email = TO_EMAIL

    daystamp, cutoff_datetime = get_daystamp_and_cutoff_datetime(cutoff_hour)

    # Check previous day first
    prev_daystamp = daystamp - datetime.timedelta(days=1)
    exists, archived = exists_and_is_archived(prev_daystamp)
    if exists and not archived:
        print("Sending notification with app usage from previous day")
        prev_db_path = get_db_path(prev_daystamp)
        prev_con = sqlite3.connect(prev_db_path)
        prev_data = (
            prev_con.cursor()
            .execute("select name, category, walltime from Aggregations")
            .fetchall()
        )

        prev_response = send_summary_email(
            prev_data,
            prev_daystamp,
            prev_db_path,
            to_email,
            from_email,
            from_email_pwd=os.environ["APP_USAGE_TRACKER_EMAIL_PWD"],
        )
        archive_log_path = ARCHIVE_LOG_PATH
        archive_db(
            prev_daystamp, prev_response, archive_log_path=archive_log_path
        )

    db_path, data = scrape()
    # If the next scheduled scrape is past the cutoff time,
    # send an aggregation email after this scrape
    if (
        datetime.datetime.now() + datetime.timedelta(minutes=interval_minutes)
    ) >= cutoff_datetime:
        print("Sending notification with app usage")
        response = send_summary_email(
            data,
            daystamp,
            db_path,
            to_email,
            from_email,
            from_email_pwd=os.environ["APP_USAGE_TRACKER_EMAIL_PWD"],
        )

        archive_log_path = ARCHIVE_LOG_PATH
        archive_db(
            db_path, daystamp, response, archive_log_path=archive_log_path
        )
