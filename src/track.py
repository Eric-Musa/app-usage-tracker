import datetime
import os
import psutil
import re
import time
from pathlib import Path
from categories import classify

BASE_DIR = Path.cwd().parent
OUTPUT_DIR = BASE_DIR / 'logs'

if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(OUTPUT_DIR, 'made:', os.path.isdir(OUTPUT_DIR))
else:
    print(OUTPUT_DIR, 'exists:', os.path.isdir(OUTPUT_DIR))


def proc_runtime(ts):
    return datetime.datetime.now() - datetime.datetime.fromtimestamp(ts)  # .strftime("%Y-%m-%d %H:%M:%S")


def log_processes(log_template='process_log_(\d+).txt', max_logs=1000):
    log_numbers = sorted(
        [int(_) for _ in re.findall(log_template, '|'.join(os.listdir(OUTPUT_DIR)))], 
        reverse=True)
        
    next_log = log_template.replace('(\d+)', '%d') % int(time.time())
    with open(OUTPUT_DIR / next_log, 'w') as f:
        for k, v in sorted(cache.items(), key=lambda x: len(x[1]), reverse=True):
            f.write('%s (%s): %d\n' % (k, v[0][2], len(v)))
    
    while len(log_numbers) > max_logs - 1:
        last_log = log_template.replace('(\d+)', '%d') % (log_numbers.pop(-1))
        os.remove(OUTPUT_DIR / last_log)
        print('removed oldest log: %s --> exists: %s' % (last_log, os.path.exists(last_log)))


if __name__ == '__main__':

    cache = {}
    
    for proc in psutil.process_iter():
        try:
            pid = proc.pid
            runtime = proc_runtime(proc.create_time())
            pname = proc.name()
            pexe = proc.exe()
            category = classify(pexe)
            p = [pid, pname, category, runtime, pexe]
            if pname not in cache:
                cache[pname] = [p]
            else:
                cache[pname].append(p)
        except psutil.AccessDenied as e:
            print(e)
    
    log_processes(max_logs=100)
