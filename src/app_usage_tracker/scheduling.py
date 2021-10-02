import datetime


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%s %s" % (DATE_FORMAT, TIME_FORMAT)

DAYSTAMP_HOUR_CUTOFF = 3  # 3 AM cutoff


def get_daystamp(cutoff=DAYSTAMP_HOUR_CUTOFF):
    daystamp = datetime.date.today()
    if datetime.datetime.now().hour == cutoff:
        return daystamp - datetime.timedelta(days=1)
    return daystamp
