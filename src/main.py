#!/usr/bin/env python

"""Find the currently active window."""

import logging
import re
import sys

from time import sleep

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
        import psutil
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
    else:
        print(f"{sys.platform=} is unknown. Please report.")
        print(sys.version)
    return active_window_name

while True:
    print("Active window: %s" % str(get_active_window()))
    sleep(1)
