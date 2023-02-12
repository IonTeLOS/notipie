# notipie
Desktop notifications and notification service with optional forwarding to WhatsApp

NotiPie & notipie-listen   

notipie-listen application on Windows runs a local (within your system) NotificationListener to receive your toast notifications.
Received notifications are forwarded to NotiPie application and shown as a special window, shown in the console (when using notipie-listen.py), written to a local log file, forwarded to WhatsApp or a combination thereof. 
NotiPie, our main application served by notipie-listen, re-imagines the way you receive notifications, messages and script dialogues from your Operating System and other applications. NotiPie is a work in progress under active development. Read more about NotiPie in its documentation.
Configure NotiPie application to get your notifications the way You want.
A separate app, mudslide, is used to materialize the WhatsApp forwarding feature (Internet access is required for this feature to work). An in-house built .exe of mudslide app is included in the box. If that doesn’t work as expected, you can install mudslide manually from npm (prior installation of nodejs and git is required). Find more about mudslide in their website --> https://github.com/robvanderleek/mudslide. 
notipie-listen will optionally attempt to find a suitable icon for the app sending the notification and use that icon when showing the notification with NotiPie. Icons are downloaded with google-images-download script as shown in their website --> https://github.com/hardikvasa/google-images-download (Internet access is required for this feature to work - fallback icon provided). 
You can activate 'focus assist' Windows feature to receive your toast notifications exclusively with NotiPie. Nevertheless, your notifications will remain accessible in your action center, unless you explicitly use the '--delete' argument. 
Attention: 
i. Make sure you have activated notifications in your settings.        
ii. To use this application you need to allow app access to your notifications in your Windows settings. iii. NotificationListener, an integrated Windows feature, is not supported in older versions of Windows.  Enjoy !
~ Get NotiPie - read more - contribute : https://github.com/iontelos/notipie ~

* NotiPie and notipie-listen have been developed initially and primarily for Linux and particularly TeLOS Linux
* Python and PyQt5 have been used to develop this app
* Create a Python virtual environment, install the modules from the corresponding requirements.txt files and build the application with pyinstaller
* mudslide has been built with pkg following instructions in the corresponding GitHub repository page
* app has been tested in Windows 10 and Windows 11 

AVAILABLE OPTIONS   
-r, --random Get your NotiPie notifications in random color and randomly placed on your screen. This option allows you to override NotiPie's settings. This is the default. 

Hint: Change the Target in the application’s shortcut in Menu - Start Menu to launch notipie-listen using different options described here. Or use the command line.  

-t, --test Test the functionality of notipie-listen by sending a test notification. In case you have NotiPie and everything works as expected, you will receive the notification (also) with NotiPie.

-q, --quit Terminate any running instance of notipie-listen.

-v, --viewlog Open your log file and exit.

-e, --empty Clear your log file and continue.

-b, --background (in the .exe application) or -c, --console (in the python script)

Don’t forward notifications to NotiPie. Use this option for debugging, reading notifications in the console, writing logs or combined with the ‘--whatsapp’ option (optional).

Attention: To read your notifications in the console use the .py script after installing python and necessary dependencies from the requirements.txt file plus any dependencies of notipie.py. Make sure you have npm and git installed to use mudslide (WhatsApp forwarding) if you don’t use the provided .exe. 

-f, --focus Start the app by showing a toast notification to remind the (optional) activation of focus assist Windows feature. By enabling focus assist in your system settings you will receive notifications only with NotiPie. Your notifications will remain accessible in the action center, unless you launch the app with the ‘--delete’ argument.

-s, --settings Open Windows notifications's settings and exit.

-g, --getapp Send a toast notification, open webpage to download main NotiPie app and exit.

-w, --whatsapp Optionally forward your incoming notifications to a WhatsApp number. Use the number including the international code (no + or 00 in the beginning) as argument or leave it blank to forward your PC notifications to your own logged in telephone number. Internet access is required to use this feature. Read more at https://github.com/robvanderleek/mudslide

-l, --logthis Specify a keyword or key-phrase (in quotes) to watch for in your incoming notifications. This can be the name of an app sending notifications or anything else you want. Messages containing this keyword or phrase will be written to the log file and marked with *. 

-a, --log Write all incoming notifications to the log file (optional). There is no need to use this option when using NotiPie, since NotiPie main application already provides this functionality.
Attention: The app can be launched with one of the arguments whatsapp, logthis and log

--login Login to use mudslide and forward incoming notifications to WhatsApp. This option opens the console for you to scan a QR code. It also opens the corresponding webpage in your browser to go through mudslide documentation. 

--logout This is a mudslide app command shortcut to logout from WhatsApp. This option will open the console to confirm the output of the command.

--noicon Don’t download icons from the Internet, always use NotiPie icon instead.

--licence Show this application's licence and exit.

-x, --export (option available in the .exe application) Copy raw script notipie-listen.py, notipie.py and gid.py plus the requirements.txt for notipie-listen.py to the same directory as the executable. This is useful if you want to use the  ‘--console’ mode, which is only available in the python script, inspect the code, make code modifications of your own or rebuild the app (pyinstaller suggested). Make a pull request in GitHub or get in touch, if you think your modifications or suggestions can benefit other people.

-d, --delete Delete incoming notifications (last one each time) from the action center.

-o, --open Open the folder where app icons are stored to view and optionally change icons.

--noinstall Do not install .exe application (available in the .exe application). Many app features will not be available by using this option.

-m, --duration Duration in minutes to run the app for. Default is long, very long.

--wiki (option available in the .exe application) Show this file and exit.

Last words: By default the app is installed in C:\Users\{username}\AppData\Roaming\Notipie. Shortcuts, including one for the WhatsApp forwarding option, are added in the Menu. The app will auto launch at system start up (WhatsApp forwarding feature will be deactivated by default). Customize this behavior according to your needs and wishes by editing the shortcuts or creating new ones and optionally including above arguments.  

———————————————————————————————————


NotiPie and notipie-listen for Windows are published under GPLv3 License 
Copyright© 2023 Ion@TeLOS. This program comes with ABSOLUTELY NO WARRANTY 
NotiPie and notipie-listen is free software and you are welcome to redistribute it under certain conditions
google-images-download and mudslide come with their own licenses. This app and the developer are not affiliated to WhatsApp
