import os
import sys
import time
import subprocess
import psutil  # maybe better for windows

import threading

from config import DATA_DIR


# TODO
# ------------
# revist this on linux, had to do some weirdness to make it work on windows
# i dont like the stream logs function and daemon
# ideally we remove this but it is good for debugging


# Stream postgres logs
def stream_logs(stream):
    for line in iter(stream.readline, ""):
        print("[postgres]", line.strip())


def shutdown_postgres():
    """safely shutdown postgres server"""
    subprocess.run(["pg_ctl", "-D", DATA_DIR, "stop", "-m", "fast"], check=False)


if __name__ == "__main__":
    print("Watchdog started. PID:", os.getpid())

    parent_pid = int(sys.argv[1])
    cmd = sys.argv[2:]

    print("Launching postgres...")
    child = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    threading.Thread(target=stream_logs, daemon=True).start()

    try:
        while True:
            # previously using oskill(paried_pid,0)
            if not psutil.pid_exists(parent_pid):  # cross platform
                print("Parent is dead. Shutting down Postgres.")
                shutdown_postgres()
                child.wait()  # wait for exit
                break
            time.sleep(1)  # wait and try again

    except KeyboardInterrupt:
        shutdown_postgres()
        child.wait()

    print("Watchdog exiting")
