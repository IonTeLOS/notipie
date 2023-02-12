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
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox


class InstallDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'NotiPie'
        self.left = 700
        self.top = 200
        self.width = 400
        self.height = 300
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        buttonReply = QMessageBox.question(
            self, 'NotiPie', "Do you want to install NotiPie?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if buttonReply == QMessageBox.Yes:
            lpro = subprocess.Popen(["mkdir", "%APPDATA%\\Notipie\\"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["mkdir", "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotiPie\\"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\notipie-listen.ico', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\notipie.png', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\nl-green.ico', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\notipie-wiki.pdf', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\notipie-wiki.pdf', '%USERPROFILE%\\Desktop\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\NotiPieListen.lnk', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\Quit.lnk', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\NotiPieListenWA.lnk', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\not_sound.wav', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\NotiPie.ini', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
            atexit.register(restart)
            atexit.register(install)
            app.quit()
        else:
            pass
            app.quit()
        self.show()


async def handler():
    application_path = os.path.dirname(os.path.realpath(sys.executable))

    destination = os.path.expandvars('%APPDATA%\\Notipie\\notipie-listen.exe')
    mydestination = Path(destination)
    if not mydestination.is_file() and not args.noinstall:
        InstallDialog()
        sys.exit(0)
    exe = "\\notipie.exe"
    pyscript = "\\notipie.py"
    if os.path.isfile(application_path + exe):
        notipie_path = str(application_path) + exe
    elif os.path.isfile(application_path + pyscript):
        notipie_path = str(application_path) + pyscript
    else:
        if not args.background:
            atexit.register(get_notipie)
            sys.exit(0)

    listener = UserNotificationListener.get_current()
    accessStatus = await listener.request_access_async()

    if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
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
        except:
            APP = "NotiPie"

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
                try:
                    response = googleimagesdownload()
                    iarguments = {"keywords": APP, "limit": 1, "format": "png", "aspect_ratio": "square",
                                  "size": "icon", "safe_search": True, "silent_mode": True, "output_directory": directory}
                    response.download(iarguments)
                    for file in glob.glob(searchpath):
                        ICON = file
                except:
                    ICON = str(Path(__file__).parent.absolute()) + \
                        '\\notipie.png'
            else:
                ICON = str(Path(__file__).parent.absolute()) + '\\notipie.png'
        else:
            for file in glob.glob(searchpath):
                ICON = file

        try:
            it = iter(text_sequence)
            TITLE = it.current.text.replace('\n', ' ')
        except:
            TITLE = " "

        try:
            next(it, None)
            if it.has_current:
                BODY = it.current.text.replace('\n', ' ')
            else:
                BODY = " "
        except:
            BODY = " "

        if not args.background:
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
        else:
            pass

        if args.whatsapp:
            internet_access = have_internet()
            if internet_access == True:
                number = args.whatsapp
                wa_notification = "PC Notification (%USERNAME%@%COMPUTERNAME%): From: " + \
                    f'{APP}' + " *Title: " + f'{TITLE}' + \
                    " *Message: " + f'{BODY}'
                mypid = str(os.getpid())
                selfIDfile = application_path + '\\notipie_listen_selfid.txt'
                if os.path.isfile(selfIDfile):
                    with open(selfIDfile, 'r') as file:
                        target = file.read().rstrip()
                        if target != mypid:
                            try:
                                kpro = subprocess.Popen(["taskkill", "/F", "/PID", target], shell=True,
                                                        stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
                            except:
                                pass
                        else:
                            pass
                else:
                    pass

                taskfile = selfIDfile
                with open(taskfile, 'w') as fet:
                    fet.write(mypid)
                if os.path.isfile(application_path + "\\mudslide.exe"):
                    try:
                        mudslide = application_path + "\\mudslide.exe"
                        wprocess = subprocess.run([mudslide, "send", number, f'{wa_notification}'], shell=True,
                                                  stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
                        if wprocess.returncode != 0:
                            whatsapp_login()
                        else:
                            pass
                    except:
                        pass
                else:
                    try:
                        wprocess = subprocess.run(
                            ["npx", "mudslide", "send", number, f'{wa_notification}'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
                        if wprocess.returncode != 0:
                            whatsapp_login()
                        else:
                            pass
                    except:
                        pass
            else:
                pass
        elif args.log:
            timestamp = datetime.now().strftime(" %H:%M - %d/%m: ")
            notification_item = timestamp + " From: " + APP + " | " + \
                "Title: " + TITLE + " | " + "Message: " + BODY + " --</br>-- "
            logfile = application_path + '\\notipie_listen_log.html'
            with open(logfile, 'a') as fo:
                fo.write(notification_item)
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
        else:
            pass

    if args.delete:
        try:
            listener.remove_notification(ID)
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
    toast('Hello prospective NotiPier !', 'Get NotiPie main application')
    webbrowser.open("https://github.com/iontelos/notipie")


def whatsapp_login():
    webbrowser.open("https://github.com/robvanderleek/mudslide")
    time.sleep(2)
    if os.path.isfile(application_path + "\\mudslide.exe"):
        try:
            os.system("start cmd /k " + application_path +
                      "\\mudslide.exe login")
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
    if os.path.isfile(application_path + "\\mudslide.exe"):
        os.system("start cmd /k " + application_path + "\\mudslide.exe logout")
    else:
        os.system("start cmd /k npx mudslide logout")


def allow_toast():
    toast('Hello prospective NotiPier !',
          'To use notipie-listen, toggle setting to : \nAllow apps to access your notifications')


def restart():
    destination = os.path.expandvars('%APPDATA%\\Notipie\\notipie-listen.exe')
    selfpath = str(Path(destination))
    startprocess = subprocess.Popen([selfpath], shell=False, stdin=None, stdout=None,
                                    stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    sys.exit(0)


def restart_wa():
    destination = os.path.expandvars('%APPDATA%\\Notipie\\notipie-listen.exe')
    selfpath = str(Path(destination))
    rprocess = subprocess.Popen([selfpath, "--whatsapp", str(args.whatsapp)], shell=False,
                                stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    sys.exit(0)


def quit():
    atexit.register(terminate)
    sys.exit(0)


def terminate():
    kprocess = subprocess.Popen(
        ["taskkill", "/im", "notipie-listen.exe", "/f"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    sys.exit(0)


def install():
    application_path = os.path.dirname(os.path.realpath(sys.executable))
    lpro = subprocess.Popen(["copy", application_path + '\\notipie-listen.exe', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\notipie.exe', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\mudslide.exe', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    lpro = subprocess.Popen(["copy", sys._MEIPASS + '\\notipie-listen.ico', '%APPDATA%\\Notipie\\'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW,)
    cprocess = subprocess.Popen(["xcopy", "%APPDATA%\\Notipie\\NotiPieListen.lnk",
                                "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotiPie\\", "/Y"], shell=True)
    ccprocess = subprocess.Popen(["xcopy", "%APPDATA%\\Notipie\\NotiPieListenWA.lnk",
                                 "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotiPie\\", "/Y"], shell=True)
    cccprocess = subprocess.Popen(["xcopy", "%APPDATA%\\Notipie\\Quit.lnk",
                                   "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotiPie\\", "/Y"], shell=True)
    lprocess = subprocess.Popen(["xcopy", "%APPDATA%\\Notipie\\NotiPieListen.lnk",
                                "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\", "/Y"], shell=True)
    toast('Hello NotiPier !', 'NotiPie has been successfully installed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="notipie-listen.exe / python notipie-listen.py",
                                     description="notipie-listen on Windows runs a local (within your own system) NotificationListener to receive your toast notifications. \
                                     Received notifications are forwarded to NotiPie, shown in the console, written to a local log file, forwarded to WhatsApp or a combination thereof. \
                                     Make sure you have activated notifications in your settings and allowed app access to notifications. \
                                     A separate app, mudslide, is used to materialize the WhatsApp forwarding feature (Internet access required). \
                                     Find more about mudslide at https://github.com/robvanderleek/mudslide. \
                                     NotiPie is the main application that re-imagines the way you receive notifications, messages and script dialogues from your Operating System and other applications. \
                                     Read more about NotiPie in https://github.com/iontelos/notipie and configure NotiPie to get your notifications the way You want! \
                                     notipie-listen will attempt to find a suitable icon for the app sending the notification to use that icon when showing the notification with NotiPie. \
                                     Icons are downloaded with google-images-download script as shown on https://github.com/hardikvasa/google-images-download \(Internet access required - fallback icon provided). \
                                     You can activate 'focus assist' Windows feature to receive your toast notifications exclusively with NotiPie. \
                                     Nevertheless, your notifications will remain accessible in the action center, unless you explicitly use the '--delete' argument. \
                                     Attention: i. Make sure you have activated notifications in your settings. \
                                     ii. To use this application you need to allow app access to your notifications in your Windows settings. \
                                     iii. NotificationListener, an integrated Windows feature, is not supported in older versions of Windows. Enjoy !",
                                     epilog="Copyright© 2023 Ion@TeLOS \nnotipie-listen is published under GPLv3 License and comes with ABSOLUTELY NO WARRANTY; \
                                     This is free software, and you are welcome to redistribute it under certain conditions; google-images-download and mudslide come with their own licences. \
                                     NotiPie and NotiPie-Listen are not affiliated to WhatsApp. \n~~ Get NotiPie - read more - contribute : https://github.com/iontelos/notipie ~~", add_help=False)
    parser.add_argument('-r', '--random', help='Get your NotiPie notifications in random color and randomly placed on your screen. \
                        This option allows you to override NotiPie\'s settings (optional).', default=False, action='store_true')
    parser.add_argument('-t', '--test', help='Test the functionality of notipie-listen by sending a test notification. \
                        In case you have NotiPie and everything works as expected, you will receive the notification (also) with NotiPie.', default=False, action='store_true')
    parser.add_argument('-q', '--quit', help='Terminate any running instance of notipie-listen.exe',
                        default=False, action='store_true')
    parser.add_argument('-v', '--viewlog', help='Open your log file and exit app',
                        default=False, action='store_true')
    parser.add_argument('-e', '--empty', help='Clear your log file and continue running the app',
                        default=False, action='store_true')
    parser.add_argument('-b', '--background', help='Do not forward notifications to NotiPie. \
                        Use this option for debugging, reading notifications in the console, writing logs or combined with --whatsapp option (optional). \
                        Attention: To read your notifications in the console use the .py script after installing python and necessary dependencies from the requirements.txt file.',
                        default=False, action='store_true')
    parser.add_argument('-f', '--focus', help='Start the app by showing a toast notification to remind the (optional) activation of focus assist Windows feature. \
                        By enabling focus assist in your system settings you will receive notifications only with NotiPie. \
                        Your notifications will remain accessible in the action center, unless you launch the app with the --delete argument.', default=False, action='store_true')
    parser.add_argument('-s', '--settings', help='Open Windows notifications\'s settings and quit app (optional).',
                        default=False, action='store_true')
    parser.add_argument('-g', '--getapp', help='Send a toast notification, open the webpage to download main NotiPie app and exit app (optional).',
                        default=False, action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-w', '--whatsapp', help='Forward incoming notifications to a WhatsApp number. \
                       Use the number including the international code (no + or 00 in the beginning) as argument or leave it blank to forward your PC notifications to your own logged in telephone number. \
                       Internet access is needed to use this feature. Read more at https://github.com/robvanderleek/mudslide (optional).', required=False, nargs='?', const='me', default='')
    group.add_argument('-l', '--logthis', help='Specify a keyword or keyphrase (in quotes) to watch for in your incoming notifications. \
                       This can be the name of an app sending notifications or anything else you want. \
                       Messages containing this keyword or phrase will be written to the log file and marked with *. (optional).', required=False, nargs='?', const='NotiPie', default='')
    group.add_argument('-a', '--log', help='Write all incoming notifications to the log file (optional). \
                       There is no need to use this option when using NotiPie, since NotiPie main application already already provides this functionality.', default=False, action='store_true')
    parser.add_argument('--login', help='Login to use mudslide and forward incoming notifications to WhatsApp. This option opens the console for you to scan a QR code. \
                        It also opens the corresponding webpage in your browser to go through mudslide documentation (optional).',  required=False, default=False, action='store_true')
    parser.add_argument('--logout', help='This is a mudslide app command shortcut to logout from WhatsApp. This option will open the console.',
                        required=False, default=False, action='store_true')
    parser.add_argument('--noicon', help='Donnot download icons from the Internet, always use NotiPie icon instead.',
                        default=False, action='store_true')
    parser.add_argument('--licence', help='Show this application\'s licence and exit.',
                        default=False, action='store_true')
    parser.add_argument('-x', '--export', help='Copy raw script notipie-listen.py and requirements.txt to the same directory as the executable. \
                        This is usefull if you want to use --console mode or make modifications.', default=False, action='store_true')
    parser.add_argument('-d', '--delete', help='Delete incoming notifications (last one each time) from the action center.',
                        default=False, action='store_true')
    parser.add_argument('-o', '--open', help='Open the folder where app icons are stored to view and optionally change icons.',
                        default=False, action='store_true')
    parser.add_argument('--noinstall', help='Do not install .exe application',
                        default=False, action='store_true')
    parser.add_argument('-m', '--duration', type=int, help='Duration in minutes to run app for.',
                        required=False, nargs='?', const='999', default='9999999')
    parser.add_argument('--wiki', help='Show a pdf file with documentation and information about this application',
                        default=False, action='store_true')

    args = parser.parse_args()

    app = QApplication(sys.argv)

    application_path = os.path.dirname(os.path.realpath(sys.executable))

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
            toast('Hello NotiPier', 'Log file cleared per your instructions')
            time.sleep(2)
    elif args.licence:
        lipath = str(Path(__file__).parent.absolute()) + '\\licence.txt'
        if os.path.isfile(lipath):
            os.system("notepad " + lipath)
        else:
            pass
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
    elif args.export:
        os.system("copy " + str(Path(__file__).parent.absolute()) +
                  '\\requirements.txt ' + application_path)
        os.system("copy " + str(Path(__file__).parent.absolute()) +
                  '\\notipie-listen.py ' + application_path)
        os.system("copy " + str(Path(__file__).parent.absolute()) +
                  '\\notipie.py ' + application_path)
        os.system("copy " + str(Path(__file__).parent.absolute()) +
                  '\\gid.py ' + application_path)
        os.system("start " + application_path)
        toast('Hello NotiPier !',
              'Copied files in directory. You can now inspect the code or run/modify/rebuild the raw .py scripts')
        sys.exit(0)
    elif args.background:
        if not args.whatsapp and not args.log and not args.logthis:
            toast('Hello NotiPier !', '--background option can only be used in combination with --whatsapp or --log or --logthis options. Exiting..')
            sys.exit(0)
        else:
            pass
    elif args.wiki:
        wikipath = str(Path(__file__).parent.absolute()) + '\\notipie-wiki.pdf'
        webbrowser.open(wikipath)
    elif args.open:
        os.system("start " + application_path + "\\appicons\\")

    mypid = str(os.getpid())
    selfIDfile = application_path + '\\notipie_listen_selfid.txt'
    taskfile = selfIDfile
    if not args.quit:
        if not args.whatsapp:
            with open(taskfile, 'w') as fit:
                fit.write(mypid)

    start = time.time()

    while time.time() - start < (args.duration * 60):
        timefrom_start = round(int(time.time() - start) / 60)
        time_left = args.duration - round(int(time.time() - start) / 60)

        asyncio.run(handler())
