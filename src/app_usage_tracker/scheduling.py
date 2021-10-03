import datetime


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%s %s" % (DATE_FORMAT, TIME_FORMAT)

DAYSTAMP_HOUR_CUTOFF = 5  # 5 AM cutoff

SCRAPE_INTERVAL = 5  # minutes


def get_daystamp_and_cutoff_datetime(cutoff=DAYSTAMP_HOUR_CUTOFF):
    """
    :param cutoff the hour of the day (24h) at which to
        rollover to the next cycle

    if the current hour is less than the cutoff hour:
        1. the previous day's cycle is still running
        2. the cutoff_datetime of the cycle is the previous
            cycle's day + 1 at the cutoff hour

    """
    daystamp = datetime.date.today()
    if datetime.datetime.now().hour < cutoff:
        daystamp -= datetime.timedelta(days=1)
    return daystamp, datetime.datetime(
        year=daystamp.year,
        month=daystamp.month,
        day=daystamp.day + 1,
        hour=cutoff,
    )
