#!/usr/bin/env python3
"""
notipie-listen.py / notipie-listen ##

NotiPie-Listen runs a DBus message loop with a callback to receive notifications on the session bus. 
Received notifications are forwarded to NotiPie, shown in the terminal, written to a log file, forwarded to WhatsApp or a combination thereof. 
Download NotiPie from : https://github.com/iontelos/notipie to get your notifications in a whole new way.
You can deactivate system notifications and receive it exclusively with NotiPie.
This script uses 'eavesdropping' by intercepting DBus signals; this works, without the need to remove your notification-daemon, which would be a no-go for many users for several obvious reasons. Enjoy !
"""

import dbus
import sys
import os
import fcntl
import atexit
import argparse
import subprocess
import webbrowser
import http.client as httplib
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from datetime import datetime


BUS = "org.freedesktop.Notifications"
OBJECT = "/org/freedesktop/Notifications"
IFACE = "org.freedesktop.Notifications"
KEYS = (
    "app_name",
    "replaces_id",
    "app_icon",
    "summary",
    "body",
    "actions",
    "hints",
    "expire_timeout",
)



def quit():    
    atexit.register(remove_kill)
    sys.exit(0)
    
def remove_kill():
    os.system("rm /tmp/notipie-listen.lock")
    os.system("pkill -9 -f notipie-listen")  
    sys.exit(0)

def get_notipie():
    print("\nNotiPie not found in the same directory as notipie-listen. \nGet NotiPie from https://github.com/iontelos/notipie and/or place NotiPie in the same directory as notipie-listen. \n\nAlternatively, to use notipie-listen without NotiPie, launch the application using the --console argument.")
    webbrowser.open("https://github.com/iontelos/notipie")
          
def check_instance():
    """
    Detect if an an instance with the label is already running, globally
    at the operating system level.

    Using `os.open` ensures that the file pointer won't be closed
    by Python's garbage collector after the function's scope is exited.

    The lock will be released when the program exits, or could be
    released if the file pointer were closed.
    """
    label="notipie-listen"
    lock_path = "/tmp/notipie-listen.lock"
    lock_file_pointer = os.open(lock_path, os.O_WRONLY | os.O_CREAT)

    try:
        fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        already_running = False
    except IOError:
        already_running = True
        print("NotiPie-Listen service is already running, exiting..") 
        sys.exit(0)
      
    return already_running

def have_internet() -> bool:
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()    
            
def main(argv):
    
    def on_call(message):
        kwargs = dict(zip(KEYS, message.get_args_list()))
        
        app = str(kwargs["app_name"])
        summary = str(kwargs["summary"])
        body = str(kwargs["body"])
        icon = str(kwargs["app_icon"])
        
        print("\nListening to dbus notifications..\n")
        print("\nI received a new notification signal from dbus: \n")
        print("From: " + app)
        print("Title: " + summary)
        print("Message: " + body)
        
        if not args.console:
            notipie_path = args.npath
            print("NotiPie path is: " + notipie_path)
        
        if args.extra and not args.console:
            options = args.extra
        else:
            options = "--dummy"
        
        hints = str(kwargs["hints"])
        urgency = "urgency'): dbus.Byte(2"   
        if hints.find(urgency) != -1:
            print("urgent notification received")
            if not args.console:
                process = subprocess.Popen([notipie_path, "--appicon", icon, "-a", app, "-t", summary, "-n", body, "-d", "--sticky", str(options)])
            if not args.noulog:
                timestamp = datetime.now().strftime(" %H:%M - %d/%m: ")
                notification_item = "-urgent- " + timestamp + " From: " + app + " | " + "Title: " + summary + " | " + "Message: " + body + " --\n\n-- "
                path = "~/.notipie_listen_log.txt"
                log_file = os.path.expanduser(path)
                with open(log_file, 'a') as f:
                    f.write(notification_item)
        else:
            expiration = round(kwargs["expire_timeout"]/1000)
            if expiration > 5:
                timeout = str(expiration)
                if not args.console:
                    process = subprocess.Popen([notipie_path, "--appicon", icon, "-a", app, "-t", summary, "-n", body, "-d", timeout, str(options)])
            else:
                if not args.console:
                    process = subprocess.Popen([notipie_path, "--appicon", icon, "-a", app, "-t", summary, "-n", body, str(options)])
        
        if args.whatsapp:
            internet_access = have_internet()
            if internet_access == True:
                number = args.whatsapp
                notification_item = "PC Notification: \nFrom: " + app + "\nTitle: " + summary + "\nMessage: " + body
                try: telprocess = subprocess.Popen(["npx", "mudslide", "send", number, notification_item])
                except : print("Something went wrong.. Please check your mudslide configuration \nRead more at: https://github.com/robvanderleek/mudslide")
            else:
                print("Reconnect to the internet to forward notifications to WhatsApp")
        
        if args.logall:
            timestamp = datetime.now().strftime(" %H:%M - %d/%m: ")
            notification_item = timestamp + " From: " + app + " | " + "Title: " + summary + " | " + "Message: " + body + " --\n\n-- "
            path = "~/.notipie_listen_log.txt"
            log_file = os.path.expanduser(path)
            with open(log_file, 'a') as f:
                f.write(notification_item)
        elif args.log:
            keyword = args.log
            everything = app + " " + summary + " " + body
            if everything.find(keyword) != -1:
                timestamp = datetime.now().strftime(" %H:%M - %d/%m: ")
                notification_item = "* " + timestamp + " From: " + app + " | " + "Title: " + summary + " | " + "Message: " + body + " --\n\n-- "
                path = "~/.notipie_listen_log.txt"
                log_file = os.path.expanduser(path)
                with open(log_file, 'a') as f:
                    f.write(notification_item)
          
    def on_any(bus, message):
        if (message.get_interface() == IFACE
            and message.get_member() == "Notify"):
            on_call(message)
        else:
            pass
    
    check_instance()

    dbus_loop = DBusGMainLoop()
    bus = dbus.SessionBus(mainloop=dbus_loop)
    bus.add_match_string_non_blocking(f"eavesdrop=true")
    bus.add_message_filter(on_any)
    proxy = bus.get_object(bus_name=BUS, object_path=OBJECT)
    iface = dbus.Interface(proxy, dbus_interface=IFACE)

    main_loop = GLib.MainLoop()
    main_loop.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = "notipie-listen", description = "NotiPie-Listen runs a DBus message loop with a callback to receive anything on a session bus. Received notifications are forwarded to NotiPie, shown in the terminal, written to a file, forwarded to WhatsApp or a combination thereof. An external app is needed for the WhatsApp option to work; find more at https://github.com/robvanderleek/mudslide . Get NotiPie from : https://github.com/iontelos/notipie . Configure NotiPie application to get your notifications in the format you wish. You can deactivate system notifications and receive it the way you choose with NotiPie-Listen. This script uses \'eavesdropping\' by intercepting dbus signals; because it works, without the need to remove your notification-daemon, which would be a no-go for many users for several obvious reasons. Enjoy !", epilog = "~~ Get NotiPie - read more - contribute : https://github.com/iontelos/notipie ~~")
    parser.add_argument('-t', '--test', help='Tests the app\'s functionality by sending a test notification with notify-send (package requirement: libnotify-bin). For example, in case you have NotiPie and everything works as expected, you will receive the notification (also) with NotiPie.', default=False, action='store_true')
    parser.add_argument('-q', '--quit', help='Removes lock file and kills any running instance of notipie-listen.', default=False, action='store_true')
    parser.add_argument('-l', '--log', help='Specify a keyword or keyphrase (in quotes) to monitor. This can be the name of an app sending notifications or anything else. Messages containing this keyword or phrase will be written to the log file. All urgent notifications will be also written to the log file, unless you use this together with the --noulog option. You can use --log and --noulog options combined to monitor only notifications containing the keyword or phrase of your choice and exclude the logging of urgent notifications not containing the keyword (optional).', required=False, nargs='?', const='NotiPie', default='')
    parser.add_argument('-r', '--readlog', help='Read your log file.', default=False, action='store_true')
    parser.add_argument('-w', '--whatsapp', help='Forward incoming notifications to a WhatsApp number. Use the number as argument or leave blank to forward your PC notifications to your own telephone number. Internet access is needed. Configure mudslide app to use this option. Follow the instructions at https://github.com/robvanderleek/mudslide (optional).', required=False, nargs='?', const='me', default='')
    parser.add_argument('--extra', help='Extra options to pass to NotiPie (optional/experimental - Attention: not all NotiPie arguments are available here).', required=False, nargs='?', const='', default='')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--console', help='Donnot forward system notifications to NotiPie. Use this option to get your notifications in the terminal, to keep a log file, to forward notifications to a WhatsApp number or to get a combination thereof (optional).', default=False, action='store_true')
    group.add_argument('-p', '--npath', help='The path to NotiPie executable or script. Default path is your ~/.local/bin/notipie (optional). Call this option without providing an argument in case you have installed NotiPie in your /usr/bin/ directory', required=False, nargs='?', const='/usr/bin/notipie', default='~/.local/bin/notipie')
    groupA = parser.add_mutually_exclusive_group()
    groupA.add_argument('-n', '--noulog', help='Don\'t log (=donnot write to the log file) your urgent notifications.', default=False, action='store_true')
    groupA.add_argument('-a', '--logall', help='Write all incoming notifications to the log file (optional).', default=False, action='store_true')
    
    args = parser.parse_args()
    
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(os.path.realpath(sys.executable))
        print("> running notipie-listen: " + application_path + "/notipie-listen")
    elif __file__:
        application_path = os.path.dirname(__file__)
        print("> running notipie-listen: " + application_path + "/notipie-listen.py")
    
    executable = "/notipie"
    pyscript = "/notipie.py"
    if os.path.isfile(application_path + executable):
        notipie_path = str(application_path) + executable
        print("Using NotiPie from: " + application_path + executable)
    elif os.path.isfile(application_path + pyscript):
        notipie_path = str(application_path) + pyscript
        
    else:
        if not args.console:
            atexit.register(get_notipie)
            sys.exit(0)
    print("Using NotiPie from: " + notipie_path)
    
    mexec = "/mudslide"
    if os.path.isfile(application_path + mexec):
        mud_path = str(application_path) + mexec
    else:
        mud_path = "npx"
    print("Attempting to use mudslide from: " + mud_path)
    
    if args.quit:
        quit()
        sys.exit(0)
    elif args.test:
        os.system("notify-send -a 'notipie-listen' -i bell -t 20000 'This is a test notification' 'In case you received it with NotiPie, it means that notipie-listen is active.'")
        sys.exit(0)
    elif args.readlog:
        path = "~/.notipie_listen_log.txt"
        log_path = os.path.expanduser(path)
        os.system("xdg-open " + log_path)
        sys.exit(0)
   
    main(sys.argv)

    
