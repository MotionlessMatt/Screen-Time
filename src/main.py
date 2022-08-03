from datetime import datetime
import logging
import os
import re
import sys

import time
import pandas as pd
import sqlite3


db = sqlite3.connect("data.db")
cur = db.cursor()

try:
    cur.execute('''CREATE TABLE screentime
                (app text, start text, end text, seconds integer)''')
except:
    pass

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG,
                    stream=sys.stdout)


def get_active_window():
    """
    Get the currently active window.

    Returns
    -------
    string :
        Name of the currently active window.
    """
    active_window_name = None
    if sys.platform in ['linux', 'linux2']:
        try:
            import wnck
        except ImportError:
            logging.info("wnck not installed")
            wnck = None
        if wnck is not None:
            screen = wnck.screen_get_default()
            screen.force_update()
            window = screen.get_active_window()
            if window is not None:
                pid = window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
        else:
            try:
                from gi.repository import Gtk, Wnck
                gi = "Installed"
            except ImportError:
                logging.info("gi.repository not installed")
                gi = None
            if gi is not None:
                Gtk.init([])  # necessary if not using a Gtk.main() loop
                screen = Wnck.Screen.get_default()
                screen.force_update()  # recommended per Wnck documentation
                active_window = screen.get_active_window()
                pid = active_window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
    elif sys.platform in ['Windows', 'win32', 'cygwin']:
        import win32gui, win32process, win32api, win32con
        window = win32gui.GetForegroundWindow()
        pid = win32process.GetWindowThreadProcessId(window)
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid[1])
            proc_name = win32process.GetModuleFileNameEx(handle, 0)
            active_proc_name = proc_name.split(".exe")[0].split("\\")[-1]
        except:
            active_proc_name = ""
        active_window_name = win32gui.GetWindowText(window)
        active_window_name = active_window_name.split(" — ")[-1]
        active_window_name = active_window_name.split(" - ")[-1]
        if active_proc_name == "explorer" and active_window_name != "":
            active_window_name = "File Explorer"
        if active_proc_name.lower() in active_window_name.lower():
            active_window_name = active_window_name
        elif active_proc_name == "javaw":
            pass
        elif active_proc_name == "ApplicationFrameHost":
            pass
        elif active_window_name == "" or active_proc_name.endswith("Host"):
            active_window_name = None
        elif active_window_name.lower().replace(" ", "") in active_proc_name.lower().replace(" ", ""):
            pass
        else:
            active_window_name = " ".join(re.sub(r"([A-Z])", r" \1", active_proc_name).split())
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        from AppKit import NSWorkspace, NSDate, NSRunLoop, NSDefaultRunLoopMode
        rl = NSRunLoop.currentRunLoop()
        active_window = NSWorkspace.sharedWorkspace().frontmostApplication()
        window_bundle_url = str(active_window.bundleURL().absoluteString())
        active_window_name = window_bundle_url.split(".app")[0].split("/")[-1].replace("%20", " ")
        date = NSDate.date()
        rl.acceptInputForMode_beforeDate_(NSDefaultRunLoopMode, date)
        if active_window_name in ["Finder", "loginwindow"]:
            active_window_name = None
    else:
        print(f"{sys.platform=} is unknown. Please report.")
        print(sys.version)
    return active_window_name

data = []
active_window = get_active_window()
start_time = time.time()
while True:
    data_size = len(data)
    try:
        time.sleep(1)
        new_window = get_active_window()
        if active_window != new_window:
            if active_window != None:
                end_time = time.time()
                seconds_elapsed = end_time - start_time
                start_date = datetime.fromtimestamp(start_time)
                end_date = datetime.fromtimestamp(end_time)
                cur.execute("INSERT INTO screentime values (?, ?, ?, ?)", (active_window, start_date, end_date, int(seconds_elapsed)))
                data.append([active_window, start_date, end_date, seconds_elapsed])
            active_window = new_window
            start_time = time.time()
    except KeyboardInterrupt:
        if active_window != None:
            end_time = time.time()
            seconds_elapsed = end_time - start_time
            start_date = datetime.fromtimestamp(start_time)
            end_date = datetime.fromtimestamp(end_time)
            cur.execute("INSERT INTO screentime values (?, ?, ?, ?)", (active_window, start_date, end_date, int(seconds_elapsed)))
            data.append([active_window, start_date, end_date, seconds_elapsed])
        break

    if len(data) != data_size:
        session_df = pd.DataFrame(data, columns=["App", "Start", "End", "Total Seconds"])
        purge = "cls" if sys.platform in ['Windows', 'win32', 'cygwin'] else "clear"
        os.system(purge)
        print(session_df.to_string())

    db.commit()

session_df = pd.DataFrame(data, columns=["App", "Start", "End", "Total Seconds"])
session_df.to_csv("data.csv")
session_df.to_json("data.json")