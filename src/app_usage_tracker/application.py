import datetime
import json
import psutil

# import random
from .categories import categorize
from .scheduling import DATETIME_FORMAT


def trim_datetime(dt):
    return dt - datetime.timedelta(microseconds=dt.microsecond)


# def bad_hash(a, b):
#     random.seed(a)
#     r1 = str(random.random())[:8]
#     random.seed(b)
#     r2 = str(random.random())[:8]
#     return int(''.join(r1.split('.') + r2.split('.')))


# def bad_hash(*seeds):
#     max_sample = int(16 / len(seeds))
#     hash = ''
#     for seed in seeds:
#         random.seed(seed)
#         hash += str(random.random()).split('.')[1][:max_sample]
#     return int(hash)


def ctime(proc: psutil.Process):
    """
    convert `Process` create_timestamp to datetime, ignoring microseconds
    """
    return trim_datetime(datetime.datetime.fromtimestamp(proc.create_time()))
    # startup = datetime.datetime.fromtimestamp(proc.create_time())
    # return startup - datetime.timedelta(microseconds=startup.microsecond)


STILL_RUNNING = "running"
STOPPED = "stopped"


class Application:
    def __init__(self, name, pids, exe, startup, shutdown) -> None:
        self.name = name
        self.pids = pids
        self.exe = exe

        if isinstance(startup, datetime.datetime):
            self.startup = startup
        else:
            self.startup = datetime.datetime.strptime(startup, DATETIME_FORMAT)
        assert self.startup.microsecond == 0

        if (
            self._pids_alive()
        ):  # first check if PIDS are running (primary source)
            self.shutdown = STILL_RUNNING
        else:
            try:  # if not running, see if passed `shutdown` is parsable
                self.shutdown = datetime.datetime.strptime(
                    shutdown, DATETIME_FORMAT
                )
            except ValueError:  # otherwise, use current time as shutdown time
                self.shutdown = datetime.datetime.now()

        self.category = categorize(self.exe)

    @classmethod
    def from_process(cls, proc: psutil.Process, assume_running=True):
        if assume_running:
            return cls(
                proc.name(), [proc.pid], proc.exe(), ctime(proc), STILL_RUNNING
            )
        else:
            shutdown = (
                STILL_RUNNING if proc.is_running() else datetime.datetime.now()
            )
            return cls(
                proc.name(), [proc.pid], proc.exe(), ctime(proc), shutdown
            )

    def add(self, proc: psutil.Process):
        assert self.shutdown == STILL_RUNNING
        assert proc.is_running() and proc.exe() == self.exe
        if proc.pid in self.pids:
            return
        else:
            self.pids.append(proc.pid)
            self.startup = min(self.startup, ctime(proc))

    def walltime(self):
        return (
            trim_datetime(datetime.datetime.now())
            if self.is_alive()
            else self.shutdown
        ) - self.startup

    def _pids_alive(self):
        pids_statuses = []
        for pid in self.pids:
            try:
                proc = psutil.Process(pid)
                pids_statuses.append(proc.is_running())
            except psutil.NoSuchProcess:
                pids_statuses.append(False)
        return any(pids_statuses)

    def is_alive(self):
        """
        Check if self.shutdown has been set yet,
        otherwise, check all cached processes for run status
        """
        if self.shutdown == STILL_RUNNING and not self._pids_alive():
            self.shutdown = datetime.datetime.now()
        return self.shutdown == STILL_RUNNING

    def as_db_record(self):
        return tuple(str(_) for _ in self.serialize().values())

    def serialize(self):
        return {
            "name": self.name,
            "category": self.category,
            "startup": self.startup.strftime(DATETIME_FORMAT),
            "shutdown": (
                datetime.datetime.now()
                if self.shutdown == STILL_RUNNING
                else self.shutdown
            ).strftime(DATETIME_FORMAT),
            "pids": self.pids,
            "exe": self.exe,
            "uid": self.exe + self.startup.strftime(DATETIME_FORMAT),
        }

    @classmethod
    def deserialize(cls, data):
        app = cls(
            data["name"],
            data["pids"],
            data["exe"],
            data["startup"],
            data["shutdown"],
        )
        assert (app.exe + app.startup.strftime(DATETIME_FORMAT)) == data["uid"]
        return app

    def save_to_json(self, save_path):
        with open(save_path, "w") as f:
            json.dump(self.serialize(), f)

    @classmethod
    def load_from_json(cls, load_path):
        with open(load_path, "r") as f:
            return cls.deserialize(json.load(f))

    def __hash__(self) -> int:
        # return hash(tuple(self.pids))
        # # if two of the same applications run at the same time, \
        # the pids will differ --> hash exe and startup instead
        return hash(self.exe) + hash(self.startup)

    def __eq__(self, o: object) -> bool:
        return self.__hash__() == o.__hash__()

    def _pids_str(self, max_pids=5):
        if len(self.pids) > max_pids:
            return " ".join(str(_) for _ in self.pids[:max_pids]) + "..."
        else:
            return " ".join(str(_) for _ in self.pids)

    def __str__(self) -> str:
        s = f"[{self.category}] "
        s += f"{self.name} ("
        s += STILL_RUNNING if self.shutdown == STILL_RUNNING else STOPPED
        s += f") started at {self.startup.strftime(DATETIME_FORMAT)} "
        s += f"(runtime: {str(self.walltime()).split('.')[0]}) "
        s += f"({len(self.pids)} pids: {self._pids_str()})"
        return s

    def __repr__(self) -> str:
        return str(self)
