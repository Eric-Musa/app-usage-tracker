import datetime
import json
import os
import psutil
import re
import time
from pathlib import Path
from categories import classify

BASE_DIR = Path.cwd().parent


def proc_runtime(ts):
    return datetime.datetime.now() - datetime.datetime.fromtimestamp(ts)  # .strftime("%Y-%m-%d %H:%M:%S")


def ctime(proc: psutil.Process):
    return datetime.datetime.fromtimestamp(proc.create_time())


STILL_RUNNING = 'running'

class Application:

    def __init__(self, name, pids, exe, startup, shutdown) -> None:
        self.name = name
        self.pids = pids
        self.exe = exe

        if isinstance(startup, datetime.datetime):
            self.startup = startup
        else:
            self.startup = datetime.datetime.strptime(startup, "%Y-%m-%d %H:%M:%S")
        
        if isinstance(shutdown, datetime.datetime) or shutdown == STILL_RUNNING:
            self.shutdown = shutdown
        else:
            self.shutdown = datetime.datetime.strptime(shutdown, "%Y-%m-%d %H:%M:%S")
        
        self.category = classify(self.exe)

    @classmethod
    def from_process(cls, proc: psutil.Process):
        shutdown = STILL_RUNNING if proc.is_running() else datetime.datetime.now()
        print(proc, shutdown)
        return cls(proc.name(), [proc.pid], proc.exe(), ctime(proc), shutdown)


    def add(self, proc: psutil.Process):
        assert self.shutdown == STILL_RUNNING
        assert proc.is_running() and proc.exe() == self.exe
        if proc.pid in self.pids:
            return
        else:
            self.pids.append(proc.pid)
            self.startup = min(self.startup, ctime(proc))
    
    def wall_time(self):
        return (datetime.datetime.now() if self.is_alive() else self.shutdown) - self.startup
    
    def is_alive(self):
        if self.shutdown == STILL_RUNNING and not any((_.is_running() and _.exe() == self.exe) for _ in [psutil.Process(pid) for pid in self.pids]):
            self.shutdown = datetime.datetime.now()
        return self.shutdown == STILL_RUNNING

    def __str__(self) -> str:
        return '[%s] %s (%d processes) started at %s (%s)' % (self.category, self.name, len(self.pids), self.startup.strftime("%Y-%m-%d %H:%M:%S"), str(self.wall_time()).split('.')[0])

    def __repr__(self) -> str:
        return str(self)

    def serialize(self):
        return {
            'name': self.name,
            'pids': self.pids,
            'exe': self.exe,
            'startup': self.startup.strftime("%Y-%m-%d %H:%M:%S"),
            'shutdown': STILL_RUNNING if self.is_alive() else self.shutdown.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def deserialize(cls, data):
        app = cls(data['name'], data['pids'], data['exe'], data['startup'], data['shutdown'])
        app.is_alive()
        return app



if __name__ == '__main__':

    applications = {}

    for proc in psutil.process_iter():
        try:
            pid = proc.pid
            name = proc.name()
            if name not in applications:
                applications[name] = Application.from_process(proc)
            else:
                applications[name].add(proc)
        except psutil.AccessDenied as e:
            print(e)
    
    ser = applications['Code.exe'].serialize()
    print(json.dumps(ser, indent=2))
    des = Application.deserialize(ser)