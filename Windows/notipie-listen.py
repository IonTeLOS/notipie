import asyncio
import sys
import os
import os.path
import time
import argparse
import subprocess
import glob
import atexit
import webbrowser
import http.client as httplib
from subprocess import CREATE_NO_WINDOW
from pathlib import Path
from datetime import datetime
from win11toast import toast
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings
from gid import googleimagesdownload


async def handler():
    application_path = os.path.dirname(__file__)

    exe = "\\notipie.exe"
    pyscript = "\\notipie.py"
    if os.path.isfile(application_path + exe):
        notipie_path = str(application_path) + exe
    elif os.path.isfile(application_path + pyscript):
        notipie_path = str(application_path) + pyscript
    else:
        if not args.console:
            atexit.register(get_notipie)
            sys.exit(0)

    mexe = "\\mudslide.exe"
    if os.path.isfile(application_path + mexe):
        mud_path = str(application_path) + mexe
    else:
        mud_path = "npx"

    listener = UserNotificationListener.get_current()
    accessStatus = await listener.request_access_async()

    if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
        print("WARNING: You have not allowed app access to notifications. \nChange your system settings and restart this application. Exiting..")
        webbrowser.open("ms-settings:privacy-notifications")
        atexit.register(allow_toast)
        sys.exit(0)

    notifications = await listener.get_notifications_async(NotificationKinds.TOAST)

    try:
        last_not = (notifications[-1])
    except:
        pass

    try:
        ID = last_not.id
    except:
        pass

    lastIDfile = application_path + '\\notipie_listen_lastid.txt'

    if os.path.isfile(lastIDfile):
        with open(lastIDfile, 'r') as file:
            data = file.read().rstrip()
    else:
        with open(lastIDfile, 'w') as file:
            file.write('0')
            data = "0"

    try:
        ID
    except NameError:
        ID = None

    if ID is None:
        pass
    elif data == str(ID):
        pass
    else:
        try:
            text_sequence = last_not.notification.visual.get_binding(
                KnownNotificationBindings.get_toast_generic()).get_text_elements()
        except:
            pass

        try:
            APP = last_not.app_info.display_info.display_name
            reporter()
            print(">   " + str(application_path) + "\\notipie-listen.py")
            print("    NotiPie path is: " + notipie_path)
            print("    Using mudslide from: " + mud_path)
            print("\nNew notification received !")
            print("\nID: " + str(ID))
            print("App Name: " + APP)
        except:
            APP = "NotiPie"
            reporter()
            print(" > " + str(application_path) + "\\notipie-listen.py")
            print("    NotiPie path is: " + notipie_path)
            print("    Using mudslide from: " + mud_path)
            print("\nNew notification received !")
            print("\nID: " + str(ID))

        directory = application_path + "\\appicons\\"
        appdirectory = directory + (APP)
        searchpath = appdirectory + '\\*.png'
        try:
            dir = os.listdir(appdirectory)
        except:
            pass

        if APP == "NotiPie" or args.noicon:
            ICON = str(Path(__file__).parent.absolute()) + '\\notipie.png'
        elif not os.path.exists(appdirectory) or len(dir) == 0:
            internet_access = have_internet()
            if internet_access == True:
                print("    no icon found, searching the Internet for a " + APP + " icon")
                try:
                    response = googleimagesdownload()
                    iarguments = {"keywords": APP, "limit": 1, "format": "png", "aspect_ratio": "square",
                                  "size": "icon", "safe_search": True, "silent_mode": True, "output_directory": directory}
                    response.download(iarguments)
                    for file in glob.glob(searchpath):
                        print("Icon: " + str(file))
                        ICON = file
                except:
                    print("    no icon found; using fallback NotiPie icon..")
                    ICON = str(Path(__file__).parent.absolute()) + \
                        '\\notipie.png'
            else:
                print("    no Internet access; using fallback NotiPie icon..")
                ICON = str(Path(__file__).parent.absolute()) + '\\notipie.png'
        else:
            print("    We already have an icon for " + APP)
            for file in glob.glob(searchpath):
                print("Icon: " + str(file))
                ICON = file

        try:
            it = iter(text_sequence)
            TITLE = it.current.text.replace('\n', ' ')
            print("Title: " + TITLE)
        except:
            TITLE = " "

        try:
            next(it, None)
            if it.has_current:
                BODY = it.current.text.replace('\n', ' ')
                print("Notification: " + BODY)
            else:
                print("    no more notification text received")
                BODY = " "
        except:
            BODY = " "

        if not args.console:
            print("    forwarding notification with ID: " +
                  str(ID) + " to NotiPie")
            if notipie_path.endswith(".py"):
                if args.random:
                    notipie_command = "python", notipie_path, "-c", "random", "--xy", "random", "-a", f'{APP}', "-t", f'{TITLE}', "-n", f'{BODY}', "--appicon", ICON
                else:
                    notipie_command = "python", notipie_path, "-a", f'{APP}', "-t", f'{TITLE}', "-n", f'{BODY}', "--appicon", ICON
                sproc = subprocess.Popen(notipie_command, shell=False, stdin=None, stdout=None,
                                         stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
                notification_id = str(ID)
                checkfile = lastIDfile
                with open(checkfile, 'w') as fi:
                    fi.write(notification_id)
                print(
                    "    Notification sent with NotiPie \n\nListening to incoming notifications..\n\n")
            else:
                if args.random:
                    notipie_command = notipie_path, "-c", "random", "--xy", "random", "-a", f'{APP}', "-t", f'{TITLE}', "-n", f'{BODY}', "--appicon", ICON
                else:
                    notipie_command = notipie_path, "-a", f'{APP}', "-t", f'{TITLE}', "-n", f'{BODY}', "--appicon", ICON
                sproc = subprocess.Popen(notipie_command, shell=False, stdin=None, stdout=None,
                                         stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
                notification_id = str(ID)
                checkfile = lastIDfile
                with open(checkfile, 'w') as fi:
                    fi.write(notification_id)
                print(
                    "    Notification sent with NotiPie  \n\nListening to incoming notifications..\n\n")
        else:
            print("    \nrunning in console mode..")

        if args.whatsapp:
            internet_access = have_internet()
            if internet_access == True:
                number = args.whatsapp
                wa_notification = "PC Notification (%USERNAME%@%COMPUTERNAME%): From: " + \
                    f'{APP}' + " *Title: " + f'{TITLE}' + \
                    " *Message: " + f'{BODY}'
                if mud_path.endswith(".exe"):
                    try:
                        wprocess = subprocess.run(
                            [mud_path, "send", number, f'{wa_notification}'], shell=True)
                        if wprocess.returncode != 0:
                            whatsapp_login()
                            print("    Login to use this feature', 'Open your WhatsApp mobile app (linked devices setting) and scan the QR code. \nRead more at: https://github.com/robvanderleek/mudslide")
                        else:
                            print(
                                "\n*    sent notification to WhatsApp number: " + number)
                    except:
                        print("    something went wrong..do you have mudslide application or npm/git installed in your system? check your mudslide configuration - read mudslide documentation at https://github.com/robvanderleek/mudslide")
                else:
                    try:
                        wprocess = subprocess.run(
                            ["npx", "mudslide", "send", number, f'{wa_notification}'], shell=True)
                        if wprocess.returncode != 0:
                            whatsapp_login()
                            print("    Login to use this feature', 'Open your WhatsApp mobile app (linked devices setting) and scan the QR code. \nRead more at: https://github.com/robvanderleek/mudslide")
                        else:
                            print(
                                "\n*    sending notification to WhatsApp number: " + number)
                    except:
                        print("    something went wrong..do you have mudslide application or npm/git installed in your system? check your mudslide configuration - read mudslide documentation at https://github.com/robvanderleek/mudslide")
            else:
                print(
                    "    Reconnect to the Internet to forward notifications to WhatsApp")
        elif args.log:
            timestamp = datetime.now().strftime(" %H:%M - %d/%m: ")
            notification_item = timestamp + " From: " + APP + " | " + \
                "Title: " + TITLE + " | " + "Message: " + BODY + " --</br>-- "
            logfile = application_path + '\\notipie_listen_log.html'
            with open(logfile, 'a') as fo:
                fo.write(notification_item)
            print("\n*    Notification written to log file")
        elif args.logthis:
            keyword = args.logthis
            everything = APP + " " + TITLE + " " + BODY
            if everything.find(keyword) != -1:
                timestamp = datetime.now().strftime(" %H:%M - %d/%m: ")
                notification_item = "* " + timestamp + " From: " + APP + " | " + \
                    "Title: " + TITLE + " | " + "Message: " + BODY + " * --</br>-- "
                logfile = application_path + '\\notipie_listen_log.html'
                with open(logfile, 'a') as fos:
                    fos.write(notification_item)
                print("\n*    Found " + args.logthis +
                      " > Notification written to log file")
        else:
            print("\n*   no WhatsApp forwarding - keeping no self log")

    if args.delete:
        try:
            listener.remove_notification(ID)
            print("\n..removing last notification from action center..")
        except:
            pass


def have_internet() -> bool:
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=3)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_notipie():
    print("\nNotiPie not found in the same directory as notipie-listen. \nGet NotiPie from https://github.com/iontelos/notipie and/or place NotiPie in the same directory as notipie-listen. \n\nAlternatively, to use notipie-listen without NotiPie, launch the application using the --console argument.")
    toast('Hello prospective NotiPier !', 'Get NotiPie main application')
    webbrowser.open("https://github.com/iontelos/notipie")


def reporter():
    if timefrom_start < 2:
        print("\nnotipie-listen© 2023 Ion@TeLOS running for less than 2 minutes\n")
    elif time_left < 2:
        print("\nnotipie-listen© 2023 Ion@TeLOS running for " + str(round(int(time.time() -
              start) / 60)) + " minutes | 1 minute or less left until auto stop\n")
    else:
        print("\nnotipie-listen© 2023 Ion@TeLOS running for " + str(round(int(time.time() -
              start) / 60)) + " minutes | " + str(time_left) + " minutes left until auto stop\n")


def whatsapp_login():
    mexe = "\\mudslide.exe"
    application_path = os.path.dirname(__file__)
    if os.path.isfile(application_path + mexe):
        mud_path = str(application_path) + mexe
    else:
        mud_path = "no-path"
    webbrowser.open("https://github.com/robvanderleek/mudslide")
    time.sleep(2)
    if mud_path.endswith(".exe"):
        try:
            os.system("start cmd /k " + application_path + "\\mudslide.exe login")
        except:
            pass
    else:
        try:
            os.system("start cmd /k npx mudslide login")
        except:
            pass
    atexit.register(restart_wa)
    atexit.register(terminate)
    sys.exit(0)


def whatsapp_logout():
    mexe = "\\mudslide.exe"
    application_path = os.path.dirname(__file__)
    if os.path.isfile(application_path + mexe):
        mud_path = str(application_path) + mexe
    else:
        mud_path = "no-path"
    if mud_path.endswith(".exe"):
        os.system("start cmd /k " + application_path + "\\mudslide.exe logout")
    else:
        os.system("start cmd /k npx mudslide logout")


def allow_toast():
    toast('Hello prospective NotiPier !',
          'To use notipie-listen, toggle setting to : \nAllow apps to access your notifications')


def restart_wa():
    application = os.path.dirname(__file__) + "\\notipie-listen.py"
    rprocess = subprocess.Popen(
        ["python", application, "--whatsapp", str(args.whatsapp)])
    sys.exit(0)


def quit():
    atexit.register(terminate)
    sys.exit(0)


def terminate():
    selfIDfile = application_path + '\\notipie_listen_selfid.txt'
    if os.path.isfile(selfIDfile):
        with open(selfIDfile, 'r') as file:
            target = file.read().rstrip()
        os.system("taskkill /F /PID " + target)
    else:
        print("    nothing to do, exiting..")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="notipie-listen.exe / python notipie-listen.py", description="notipie-listen on Windows runs a local (within your own system) NotificationListener to receive your toast notifications. \
            Received notifications are forwarded to NotiPie, shown in the console, written to a local log file, forwarded to WhatsApp or a combination thereof. \
            Make sure you have activated notifications in your settings and allowed app access to notifications. A separate app, mudslide, is used to materialize the WhatsApp forwarding feature (Internet access required). \
            Find more about mudslide at https://github.com/robvanderleek/mudslide. NotiPie is the main application that re-imagines the way you receive notifications, messages and script dialogues from your Operating System and other applications. \
            Read more about NotiPie in https://github.com/iontelos/notipie and configure NotiPie to get your notifications the way You want! notipie-listen will attempt to find a suitable icon for the app \
            sending the notification to use that icon when showing the notification with NotiPie. Icons are downloaded with google-images-download script as shown on https://github.com/hardikvasa/google-images-download \
            (Internet access required - fallback icon provided). You can activate 'focus assist' Windows feature to receive your toast notifications exclusively with NotiPie. Nevertheless, your notifications will remain accessible in the action center, \
            unless you explicitly use the '--delete' argument. Attention: i. Make sure you have activated notifications in your settings. ii. To use this application you need to allow app access to your notifications in your Windows settings. \
            iii. NotificationListener, an integrated Windows feature, is not supported in older versions of Windows. Enjoy !", epilog="Copyright© 2023 Ion@TeLOS \nnotipie-listen is published under GPLv3 License and comes with ABSOLUTELY NO WARRANTY; \
            This is free software, and you are welcome to redistribute it under certain conditions; google-images-download and mudslide come with their own licences. NotiPie and NotiPie-Listen are not affiliated to WhatsApp. \
            \n~~ Get NotiPie - read more - contribute : https://github.com/iontelos/notipie ~~")
    parser.add_argument('-r', '--random', help='Get your NotiPie notifications in random color and randomly placed on your screen. This option allows you to override NotiPie\'s settings (optional).', default=False, action='store_true')
    parser.add_argument('-t', '--test', help='Test the functionality of notipie-listen by sending a test notification. In case you have NotiPie and everything works as expected, you will receive the notification (also) with NotiPie.', default=False, action='store_true')
    parser.add_argument('-q', '--quit', help='Terminate any running instance of notipie-listen',
                        default=False, action='store_true')
    parser.add_argument('-v', '--viewlog', help='Open your log file and exit',
                        default=False, action='store_true')
    parser.add_argument('-e', '--empty', help='Clear your log file and continue',
                        default=False, action='store_true')
    parser.add_argument('-c', '--console', help='Do not forward notifications to NotiPie. Use this option for debugging, reading notifications in the console, writing logs or combined with --whatsapp option (optional).', default=False, action='store_true')
    parser.add_argument('-f', '--focus', help='Start the app by showing a toast notification to remind the (optional) activation of focus assist Windows feature. By enabling focus assist in your system settings you will receive notifications only with NotiPie. Your notifications will remain accessible in the action center, unless you launch the app with the --delete argument.', default=False, action='store_true')
    parser.add_argument('-s', '--settings', help='Open Windows notifications\'s settings and quit app (optional).',
                        default=False, action='store_true')
    parser.add_argument('-g', '--getapp', help='Send a toast notification, open the webpage to download main NotiPie app and exit app (optional).',
                        default=False, action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-w', '--whatsapp', help='Forward incoming notifications to a WhatsApp number. Use the number including the international code (no + or 00 in the beginning) as argument or leave it blank to forward your PC notifications to your own logged in telephone number. \
                       Internet access is needed to use this feature. Read more at https://github.com/robvanderleek/mudslide (optional).', required=False, nargs='?', const='me', default='')
    group.add_argument('-l', '--logthis', help='Specify a keyword or keyphrase (in quotes) to watch for in your incoming notifications. This can be the name of an app sending notifications or anything else you want. Messages containing this keyword or phrase will be written to the log file and marked with *. (optional).', required=False, nargs='?', const='NotiPie', default='')
    group.add_argument('-a', '--log', help='Write all incoming notifications to the log file (optional). There is no need to use this option when using NotiPie, since NotiPie main application already already provides this functionality.', default=False, action='store_true')
    parser.add_argument('--login', help='Login to use mudslide and forward incoming notifications to WhatsApp. This option opens the console for you to scan a QR code. It also opens the corresponding webpage in your browser to go through mudslide documentation (optional).',  required=False, default=False, action='store_true')
    parser.add_argument('--logout', help='This is a mudslide app command shortcut to logout from WhatsApp. This option will open the console.',
                        required=False, default=False, action='store_true')
    parser.add_argument('--noicon', help='Donnot download icons from the Internet, always use NotiPie icon instead.',
                        default=False, action='store_true')
    parser.add_argument('--licence', help='Show this application\'s licence and exit.',
                        default=False, action='store_true')
    parser.add_argument('-o', '--open', help='Open the folder where app icons are stored to view and optionally change icons.',
                        default=False, action='store_true')
    parser.add_argument('-d', '--delete', help='Delete incoming notifications (last one each time) from the action center.',
                        default=False, action='store_true')
    parser.add_argument('-m', '--duration', type=int, help='Duration in minutes to run app for.',
                        required=False, nargs='?', const='999', default='9999999')

    args = parser.parse_args()

    application_path = os.path.dirname(__file__)

    if args.quit:
        quit()
        sys.exit(0)
    elif args.test:
        toast('Hello NotiPier',
              'In case you received this with NotiPie.. \neverything works as expected !')
        sys.exit(0)
    elif args.viewlog:
        logpath = application_path + '\\notipie_listen_log.html'
        webbrowser.open(logpath)
        sys.exit(0)
    elif args.empty:
        logpath = application_path + '\\notipie_listen_log.html'
        timestamp = datetime.now().strftime(" %H:%M - %d/%m ")
        with open(logpath, 'w') as file:
            file.write('<b>cleared logs at: </b>' + timestamp + '</br>')
            print("    cleared log file, continuing..")
            toast('Hello NotiPier', 'Log file cleared per your instructions')
            time.sleep(2)
    elif args.licence:
        lipath = str(Path(__file__).parent.absolute()) + '\\licence.txt'
        if os.path.isfile(lipath):
            os.system("notepad " + lipath)
            print("\nnotipie-listen for Windows \n\nCopyright© 2023 Ion@TeLOS. \nThis program comes with ABSOLUTELY NO WARRANTY; This is free software, and you are welcome to redistribute it under certain conditions; google-images-download and mudslide come with their own licences. \nUse this application for good purpose! \n\n~~ Get NotiPie - read more - contribute : https://github.com/iontelos/notipie ~~")
        else:
            print("\nnotipie-listen for Windows is published under GPLv3 License \n\nCopyright© 2023 Ion@TeLOS. \nThis program comes with ABSOLUTELY NO WARRANTY; This is free software, and you are welcome to redistribute it under certain conditions; google-images-download and mudslide come with their own licences. \nUse this application for good purpose! \n\n~~ Get NotiPie - read more - contribute : https://github.com/iontelos/notipie ~~")
        time.sleep(2)
        sys.exit(0)
    elif args.focus:
        toast('notipie-listen is starting..',
              'You can now activate focus assist mode', on_click='ms-settings:quiethours')
        webbrowser.open("ms-settings:quiethours")
    elif args.settings:
        webbrowser.open("ms-settings:notifications")
        sys.exit(0)
    elif args.getapp:
        get_notipie()
        sys.exit(0)
    elif args.login:
        whatsapp_login()
        sys.exit(0)
    elif args.logout:
        whatsapp_logout()
        sys.exit(0)
    elif args.open:
        os.system("start " + application_path + "\\appicons\\")

    mypid = str(os.getpid())
    #print("PID: " + mypid)
    selfIDfile = application_path + '\\notipie_listen_selfid.txt'
    taskfile = selfIDfile
    if not args.quit:
        with open(taskfile, 'w') as fit:
            fit.write(mypid)

    start = time.time()
    while time.time() - start < (args.duration * 60):
        timefrom_start = round(int(time.time() - start) / 60)
        time_left = args.duration - round(int(time.time() - start) / 60)

        asyncio.run(handler())
