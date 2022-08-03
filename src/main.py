#!/usr/bin/env python

"""Find the currently active window."""

import logging
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
        import win32gui
        window = win32gui.GetForegroundWindow()
        active_window_name = win32gui.GetWindowText(window)
        active_window_name = active_window_name.split(" - ")[-1]
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