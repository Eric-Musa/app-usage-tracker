FROM_EMAIL = "eric.musa.app.usage.tracker@gmail.com"
TO_EMAIL = "eric.musa17@gmail.com"


if __name__ == "__main__":
    import datetime
    from email.message import EmailMessage
    import logging
    import os
    from pathlib import Path
    import platform
    import shutil
    import smtplib
    from app_usage_tracker import (
        scrape,
        get_daystamp_and_cutoff_datetime,
        DATE_FORMAT,
        DAYSTAMP_HOUR_CUTOFF,
        SCRAPE_INTERVAL,
    )

    db_path, data = scrape()
    longest_app_name = max(len(_[0]) for _ in data)
    longest_cat_name = max(len(_[1]) for _ in data)
    # scrape_data_message = '\n'.join([f'{name.center(longest_app_name)} \
    # {("["+category+"]").center(longest_cat_name+2)}: {walltime}' \
    # for name, category, walltime in data])
    scrape_data_message = "\n".join(["%s [%s]: %s" % _ for _ in data])
    print(scrape_data_message)

    # cutoff = 11  # 2:00pm
    # interval = 15
    # daystamp, cutoff_datetime = \
    # get_daystamp_and_cutoff_datetime(cutoff=cutoff)
    # print(cutoff, interval, daystamp, cutoff_datetime, \
    # datetime.datetime.now() + \
    # datetime.timedelta(minutes=interval) >= cutoff_datetime)

    # cutoff = 15  # 2:00pm
    # interval = 5
    # daystamp, cutoff_datetime = \
    # get_daystamp_and_cutoff_datetime(cutoff=cutoff)
    # print(cutoff, interval, daystamp, cutoff_datetime, \
    # datetime.datetime.now() + \
    # datetime.timedelta(minutes=interval) >= cutoff_datetime)

    # cutoff = 15  # 2:00pm
    # interval = 15
    # daystamp, cutoff_datetime = \
    # get_daystamp_and_cutoff_datetime(cutoff=cutoff)
    # print(cutoff, interval, daystamp, cutoff_datetime, \
    # datetime.datetime.now() + \
    # datetime.timedelta(minutes=interval) >= cutoff_datetime)

    # exit()

    cutoff_hour = DAYSTAMP_HOUR_CUTOFF
    interval_minutes = SCRAPE_INTERVAL

    daystamp, cutoff_datetime = get_daystamp_and_cutoff_datetime(cutoff_hour)

    # If the next scheduled scrape is past the cutoff time,
    # send an aggregation email after this scrape
    if (
        datetime.datetime.now() + datetime.timedelta(minutes=interval_minutes)
    ) >= cutoff_datetime:
        print("Sending notification with app usage")
        msg = EmailMessage()
        msg[
            "Subject"
        ] = f"App Usage on {platform.node()} for \
            {daystamp.strftime(DATE_FORMAT)}"
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(scrape_data_message)

        s = smtplib.SMTP("smtp.gmail.com:587")
        s.ehlo()
        s.starttls()
        s.login(FROM_EMAIL, os.environ["APP_USAGE_TRACKER_EMAIL_PWD"])

        response = s.send_message(msg)
        if response:
            logging.warn(
                "SMTP email response returned the following: " + str(response)
            )

        s.quit()
        print("archiving database")
        archive_db_path = Path(str(db_path.stem).replace(".db", "_archive.db"))
        shutil.move(db_path, archive_db_path)
