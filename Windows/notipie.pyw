import os
import sys
import random
import argparse
import subprocess
import psutil
import atexit
import webbrowser
import inspect
import http.client as httplib
from subprocess import CREATE_NO_WINDOW
from datetime import datetime, timedelta
from pathlib import Path
from math import floor
from langdetect import detect, DetectorFactory
from gtts import gTTS
from googletrans import Translator
from quoters import Quote
from playsound import playsound
import inscriptis
import requests
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit, QFileDialog, QMenu, QTextEdit, QGraphicsOpacityEffect, QSystemTrayIcon, QAction, QComboBox, QCheckBox, QSlider, QFontDialog, QColorDialog, QDateTimeEdit, QSplitter, QFrame
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize, QRectF, QPropertyAnimation, QEasingCurve, QSettings, QUrl, QFileInfo, QDir, pyqtSlot, QEvent, QTime
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QPalette, QColor, QPainterPath, QRegion, QCursor, QPainter, QPixmap, QPolygon, QFontMetricsF, QPen
from qtwidgets import AnimatedToggle
import qtawesome as qta


class MostReadableColor():
    def getLuminance(self, color):
        """ get color luminance.

        Convert color RGB values to gamma adjusted normalized rgb values
        then combine them using sRGB constants (rounded to 4 places).
        """
        r, g, b, a = QColor(color).getRgb()
        l = ((r/255)**2.2)*0.2126 + ((g/255)**2.2)*0.7151 + \
            ((b/255)**2.2)*0.0721
        return(l)

    def getContrastRation(self, color1, color2):
        l1 = self.getLuminance(color1)
        l2 = self.getLuminance(color2)
        cr = (l1 + .05)/(l2+.05) if l1 > l2 else (l2+.05)/(l1 + .05)
        return(cr)

    def getMostReadable(self, color):
        cr = []
        for c in QColor.colorNames():
            if c == 'transparent':
                continue
            cr.append([self.getContrastRation(color, c), c])
        sorted_cr = sorted(cr, reverse=True)
        return(sorted_cr[0][1])

    def find_it(color):
        mrc = MostReadableColor()
        best_contrast_color = mrc.getMostReadable(color)
        return best_contrast_color


class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__()

        def get_script_dir(follow_symlinks=True):
            if getattr(sys, 'frozen', False):
                path = os.path.abspath(sys.executable)
            else:
                path = inspect.getabsfile(get_script_dir)
            if follow_symlinks:
                path = os.path.realpath(path)
            return path
        self.ish = str(get_script_dir())

        self.setObjectName("Settings")
        self.setWindowTitle('NotiPie Settings')
        self.setWindowIcon(qta.icon("mdi.cog"))
        self.timestamp = datetime.now().strftime(" %H:%M - %d/%m")

        screen = app.primaryScreen()
        rect = screen.availableGeometry()
        conf_file = QDir.homePath() + "\\AppData\\Roaming\\Notipie\\NotiPie.ini"

        self.instructions = "Get your notifications the way you want."
        self.instructions_label = QLabel(self.instructions)
        self.instructions_label.setFont(QFont('FontAwesome', 12, QFont.Bold))
        self.instructions_label.setTextFormat(Qt.RichText)
        self.instructions_label.setOpenExternalLinks(True)
        self.instructions_label.setWordWrap(True)

        self.ltedit = QLineEdit()
        self.ltedit.setClearButtonEnabled(True)

        instr_direct = "Choose where on your screen to get notifications"
        self.instr_dir = QLabel(instr_direct)
        self.instr_dir.setFont(QFont('FontAwesome', 10))
        self.instr_dir.setTextFormat(Qt.PlainText)
        self.instr_dir.setWordWrap(True)
        self.instr_dir.setStyleSheet("QLabel { color: cyan; }")

        self.orient_combo = QComboBox(self)
        self.orient_combo.setFixedSize(QSize(130, 35))
        self.orientations = ['north', 'ne', 'nw', 'south', 'se',
                             'sw', 'west', 'east', 'center', 'maximized', 'random']
        for orientation in self.orientations:
            self.orient_combo.addItem(orientation)
        self.orient_combo.activated.connect(self.orientation_change)

        instr_ling = "Choose what language you want your notifications translated to (requires internet)"
        self.instr_lingua = QLabel(instr_ling)
        self.instr_lingua.setFont(QFont('FontAwesome', 10))
        self.instr_lingua.setTextFormat(Qt.PlainText)
        self.instr_lingua.setWordWrap(True)
        self.instr_lingua.setStyleSheet("QLabel { color: cyan; }")

        self.lingua_combo = QComboBox(self)
        self.lingua_combo.setFixedSize(QSize(130, 35))
        self.languages = ['af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'haw', 'iw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km',
                          'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']
        for language in self.languages:
            self.lingua_combo.addItem(language)
        self.lingua_combo.activated.connect(self.language_change)

        instr_siz = "Size of notifications' window"
        self.instr_size = QLabel(instr_siz)
        self.instr_size.setFont(QFont('FontAwesome', 10))
        self.instr_size.setTextFormat(Qt.PlainText)
        self.instr_size.setWordWrap(True)
        self.instr_size.setStyleSheet("QLabel { color: cyan; }")

        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(int(rect.width() / 4))
        self.sl.setMaximum(int(rect.width() / 2))
        lines = [line for line in open(conf_file, 'r')]
        for line in lines:
            if line.startswith('size='):
                sizeValue = line.removeprefix('size=').strip()
                try:
                    self.sl.setValue(int(sizeValue))
                except:
                    self.sl.setValue(500)

        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(50)
        self.sl.valueChanged.connect(self.size_setting)

        self.trans_check = QCheckBox("Translate Notifications")
        self.trans_check.setFixedWidth(200)
        with open(conf_file) as conf:
            if 'translate=True' in conf.read():
                self.trans_check.setChecked(True)
        self.trans_check.stateChanged.connect(self.trans_setting)

        self.randomcolor_check = QCheckBox(
            "Random-colored background (overrides color setting)")
        self.randomcolor_check.setFixedWidth(200)
        with open(conf_file) as conf:
            if 'randomcolor=True' in conf.read():
                self.randomcolor_check.setChecked(True)
        self.randomcolor_check.stateChanged.connect(self.randomcolor_setting)

        self.log_dir = QLabel("Keep notification history")
        self.log_dir.setFont(QFont('FontAwesome', 10))
        self.log_dir.setWordWrap(True)
        self.log_dir.setStyleSheet("QLabel { color: cyan; }")

        self.log_check = AnimatedToggle()
        self.log_check.setFixedWidth(60)
        with open(conf_file) as conf:
            if 'log=True' in conf.read():
                self.log_check.setChecked(True)
        self.log_check.stateChanged.connect(self.log_setting)

        self.anim_dir = QLabel("Motion-animated notifications")
        self.anim_dir.setFont(QFont('FontAwesome', 10))
        self.anim_dir.setWordWrap(True)
        self.anim_dir.setStyleSheet("QLabel { color: cyan; }")

        self.anim_check = AnimatedToggle()
        self.anim_check.setFixedWidth(60)
        with open(conf_file) as conf:
            if 'animation=True' in conf.read():
                self.anim_check.setChecked(True)
        self.anim_check.stateChanged.connect(self.animation_setting)

        self.speak_dir = QLabel("Read aloud notifications (requires internet)")
        self.speak_dir.setFont(QFont('FontAwesome', 10))
        self.speak_dir.setWordWrap(True)
        self.speak_dir.setStyleSheet("QLabel { color: cyan; }")

        self.speak_check = AnimatedToggle()
        self.speak_check.setFixedWidth(60)
        with open(conf_file) as conf:
            if 'spoken=True' in conf.read():
                self.speak_check.setChecked(True)
        self.speak_check.stateChanged.connect(self.spoken_setting)

        self.sq_check = QCheckBox("Show square-shaped windows")
        with open(conf_file) as conf:
            if 'squared=True' in conf.read():
                self.sq_check.setChecked(True)
        self.sq_check.stateChanged.connect(self.square_setting)

        self.fram_check = QCheckBox("Notifications with window controls")
        with open(conf_file) as conf:
            if 'frame=True' in conf.read():
                self.fram_check.setChecked(True)
        self.fram_check.stateChanged.connect(self.framed_setting)

        self.sound_check = QCheckBox("Play no notification sounds")
        with open(conf_file) as conf:
            if 'nosound=True' in conf.read():
                self.sound_check.setChecked(True)
        self.sound_check.stateChanged.connect(self.nosound_setting)

        self.opa_dir = QLabel("Window transparency")
        self.opa_dir.setFont(QFont('FontAwesome', 10))
        self.opa_dir.setWordWrap(True)
        self.opa_dir.setStyleSheet("QLabel { color: cyan; }")

        self.opa_combo = QComboBox(self)
        self.opa_combo.setFixedSize(QSize(130, 35))
        self.opacities = ['0.85', '0.30', '0.35', '0.40', '0.45', '0.50', '0.55',
                          '0.60', '0.65', '0.70', '0.75', '0.80', '0.85', '0.90', '0.95', '1']
        for opacity in self.opacities:
            self.opa_combo.addItem(opacity)
        self.opa_combo.activated.connect(self.opacity_setting)

        self.dura_dir = QLabel("Duration in seconds")
        self.dura_dir.setFont(QFont('FontAwesome', 10))
        self.dura_dir.setWordWrap(True)
        self.dura_dir.setStyleSheet("QLabel { color: cyan; }")

        self.dura_combo = QComboBox(self)
        self.dura_combo.setFixedSize(QSize(130, 35))
        self.durations = ['10', '1', '3', '5', '7', '9',
                          '15', '30', '60', '120', '900', '99999']
        for duration in self.durations:
            self.dura_combo.addItem(duration)
        self.dura_combo.activated.connect(self.duration_setting)

        self.sound_btn = QPushButton()
        self.sound_btn.clicked.connect(self.choose_sound)
        self.sound_btn.setIcon(qta.icon("fa5.bell"))
        self.sound_btn.setIconSize(QSize(16, 16))
        self.sound_btn.setText("Notification sound")

        self.service_dir = QLabel("NOTIFICATION SERVICE")
        self.service_dir.setFont(QFont('FontAwesome', 12))
        self.service_dir.setStyleSheet("QLabel { color: cyan; }")

        self.service_check = AnimatedToggle()
        self.service_check.setFixedWidth(60)
        with open(conf_file) as conf:
            if 'service=True' in conf.read() or os.path.isfile("/tmp/notipie-listen.lock") and 'linux' in sys.platform:
                self.service_check.setChecked(True)
        self.service_check.stateChanged.connect(self.service_setting)

        self.remi_dir = QLabel("Show reminder after ... seconds")
        self.remi_dir.setFont(QFont('FontAwesome', 10))
        self.remi_dir.setWordWrap(True)
        self.remi_dir.setStyleSheet("QLabel { color: cyan; }")

        self.remi_spin = QDateTimeEdit()
        self.remi_spin.setDisplayFormat("HH:mm")
        self.remi_spin.timeChanged.connect(self.reminderdelay_setting)

        self.remi_btn = QPushButton()
        self.remi_btn.setIcon(qta.icon("mdi.reminder"))
        self.remi_btn.setIconSize(QSize(16, 16))
        self.remi_btn.setText("Set reminder text")
        self.remi_btn.setToolTip(
            'write text for reminder in textbox and click button')
        self.remi_btn.installEventFilter(self)
        self.remi_btn.clicked.connect(self.remindertext_setting)

        self.block_btn = QPushButton()
        self.block_btn.setIcon(qta.icon("mdi.block-helper"))
        self.block_btn.setIconSize(QSize(16, 16))
        self.block_btn.setText("Block app")
        self.block_btn.setToolTip(
            'write name of app to block in textbox and click button')
        self.block_btn.installEventFilter(self)
        self.block_btn.clicked.connect(self.blocksenderapp_setting)

        self.font_btn = QPushButton('Choose text font', self)
        self.font_btn.setIcon(qta.icon("mdi.format-font"))
        self.font_btn.setToolTip('select font and font size')
        self.font_btn.clicked.connect(self.on_fontclick)

        self.hist_btn = QPushButton()
        self.hist_btn.setIcon(qta.icon("mdi.history"))
        self.hist_btn.setIconSize(QSize(16, 16))
        self.hist_btn.setText("Show logs")
        self.hist_btn.setToolTip('click to show notification history')
        self.hist_btn.clicked.connect(self.histo)

        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(qta.icon("ri.delete-bin-7-line"))
        self.clear_btn.setIconSize(QSize(16, 16))
        self.clear_btn.setText("Clear logs")
        self.clear_btn.setToolTip('click to clear notification history')
        self.clear_btn.clicked.connect(self.clear_histo)

        self.bcolor_btn = QPushButton('Select main color', self)
        self.bcolor_btn.setIcon(qta.icon("mdi.format-color-fill"))
        self.bcolor_btn.setToolTip('choose window color')
        self.bcolor_btn.clicked.connect(self.on_bcolorclick)

        self.vlayout = QVBoxLayout()
        self.vlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # self.vlayout.addWidget(self.instructions_label)
        self.vlayout.addWidget(self.ltedit)
        self.vlayout.addWidget(self.randomcolor_check)
        self.vlayout.addWidget(self.log_dir)
        self.vlayout.addWidget(self.log_check)
        self.vlayout.addWidget(self.hist_btn)
        self.vlayout.addWidget(self.clear_btn)
        self.vlayout.addWidget(self.anim_dir)
        self.vlayout.addWidget(self.anim_check)
        self.vlayout.addWidget(self.speak_dir)
        self.vlayout.addWidget(self.speak_check)
        self.vlayout.addWidget(self.sq_check)
        self.vlayout.addWidget(self.fram_check)
        self.vlayout.addWidget(self.sound_check)
        self.vlayout.addWidget(self.instr_dir)
        self.vlayout.addWidget(self.orient_combo)
        self.vlayout.addWidget(self.instr_size)
        self.vlayout.addWidget(self.sl)
        self.vlayout.addWidget(self.remi_dir)
        self.vlayout.addWidget(self.remi_spin)

        self.volayout = QVBoxLayout()
        self.volayout.addWidget(self.service_dir)
        self.volayout.addWidget(self.service_check)
        self.volayout.addWidget(self.trans_check)
        self.volayout.addWidget(self.instr_lingua)
        self.volayout.addWidget(self.lingua_combo)
        self.volayout.addWidget(self.opa_dir)
        self.volayout.addWidget(self.opa_combo)
        self.volayout.addWidget(self.dura_dir)
        self.volayout.addWidget(self.dura_combo)
        self.volayout.addWidget(self.block_btn)
        self.volayout.addWidget(self.remi_btn)
        self.volayout.addWidget(self.font_btn)
        self.volayout.addWidget(self.bcolor_btn)
        self.volayout.addWidget(self.sound_btn)
        self.leftWidget = QWidget()
        self.rightWidget = QWidget()
        self.leftWidget.setLayout(self.vlayout)
        self.rightWidget.setLayout(self.volayout)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.leftWidget)
        self.splitter.addWidget(self.rightWidget)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.splitter)
        self.allayout = QVBoxLayout()
        self.allayout.addWidget(self.instructions_label)
        self.instructions_label.setAlignment(Qt.AlignCenter)
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setLineWidth(20)
        self.allayout.addWidget(self.separator)
        self.allayout.addLayout(self.hbox)
        self.setLayout(self.allayout)

    def clear_histo(self):
        historyfile = QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-log.html"
        with open(historyfile, 'r+') as historyfileclear:
            historyfileclear.truncate(0)
        process = subprocess.Popen(
            [self.ish, "-t", "Success !", "-n", "Notifications cleared"], shell=True, stdin=None, stdout=None,
                                   stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)

    def histo(self):
        process = subprocess.Popen([self.ish, "-a", "NotiPie", "-t", "Notification History", "-n", "Viewed", "-x", "notipie.py --duration 0 -i mdi6.progress-wrench --clearlog",
                                   "--delay", "1", "--tooltip", "Clear history", "-i", "msc.clear-all", "--viewlog", "--maximized", "--duration", "600"], shell=True, stdin=None, stdout=None,
                                   stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)

    def eventFilter(self, object, event):
        if object == self.block_btn and event.type() == QEvent.HoverMove:
            self.instructions_label.setText(
                "write the name of the app to block below and click the button")
            return True
        elif object == self.remi_btn and event.type() == QEvent.HoverMove:
            self.instructions_label.setText(
                "write the text for the reminder below and click the button")
            return True
        return False

    def service_setting(self, state):
        if state == Qt.Checked and 'linux' in sys.platform:
            os.system("notipie-listen --npath " + self.ish + " &")
            NotifierWidget().settings.setValue('service', "True")
            self.instructions_label.setText("Notification service ON")
            self.service_dir.setText("Service is ON")
        else:
            NotifierWidget().settings.setValue('service', "False")
            self.instructions_label.setText(
                "You chose to deactivate notification service")
            self.service_dir.setText("Service is OFF")
            if 'linux' in sys.platform:
                os.system(
                    "rm /tmp/notipie-listen.lock && notipie-listen --quit &")

    def choose_sound(self):
        self.sound_selector = QFileDialog()
        self.filedir, _ = self.sound_selector.getOpenFileName(
            None, "Choose Notification Sound File", "", "All Files (*);;Sound Files (*.wav)")
        url = QUrl.fromLocalFile(self.filedir)
        soundfilename = QFileInfo(self.filedir).filePath()
        NotifierWidget().settings.setValue('soundfile', str(soundfilename))
        self.instructions_label.setText(
            "You chose: " + str(soundfilename) + " playing it now..")
        if NotifierWidget().settings.value('soundfile') is not None:
            not_sound = NotifierWidget().settings.value('soundfile')
        else:
            not_sound = QDir.homePath() + r'\AppData\Roaming\Notipie\not_sound.wav'
        playsound(not_sound)

    def animation_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('animation', "True")
            self.instructions_label.setText(
                "You chose to show motion-animated notifications")
            self.anim_dir.setText("Animation is ON")
        else:
            NotifierWidget().settings.setValue('animation', "False")
            self.instructions_label.setText(
                "You chose to deactivate notifications' animation")
            self.anim_dir.setText("Animation is OFF")

    def randomcolor_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('randomcolor', "True")
            self.instructions_label.setText(
                "You chose to get random-colored notifications")
        else:
            NotifierWidget().settings.setValue('randomcolor', "False")
            self.instructions_label.setText(
                "You chose to deactivate random-colored notifications")

    def trans_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('translate', "True")
            self.instructions_label.setText(
                "You chose to translate notifications")
        else:
            NotifierWidget().settings.setValue('translate', "False")
            self.instructions_label.setText(
                "You chose to deactivate notifications' translation")

    def log_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('log', "True")
            self.instructions_label.setText("You chose to write history")
            self.log_dir.setText("History is ON")
        else:
            NotifierWidget().settings.setValue('log', "False")
            self.instructions_label.setText(
                "You chose to deactivate notification history")
            self.log_dir.setText("History is OFF")

    def spoken_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('spoken', "True")
            self.instructions_label.setText(
                "You chose to have your notifications read aloud (internet access required)")
            self.speak_dir.setText("TTS is ON")
        else:
            NotifierWidget().settings.setValue('spoken', "False")
            self.instructions_label.setText(
                "You chose to deactivate TTS feature")
            self.speak_dir.setText("TTS is OFF")

    @pyqtSlot()
    def on_bcolorclick(self):
        color = QColorDialog.getColor()
        NotifierWidget().settings.setValue('color', str(color.name()))
        self.instructions_label.setText(
            "You chose " + str(color.name()) + " as background color")

    @pyqtSlot()
    def on_fontclick(self):
        if not self.font:
            self.font = QFont()
        fd = QFontDialog.getFont()

        if fd[1]:

            self.font = QFont()
            self.font.setFamily(fd[0].family())
            NotifierWidget().settings.setValue('font', fd[0].family())
            self.font.setPointSize(fd[0].pointSize())
            NotifierWidget().settings.setValue('fontSize', fd[0].pointSize())

    def square_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('squared', "True")
            self.instructions_label.setText(
                "You chose to show square notifications")
        else:
            NotifierWidget().settings.setValue('squared', "False")
            self.instructions_label.setText(
                "You chose to show normal notifications")

    def framed_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('frame', "True")
            self.instructions_label.setText(
                "You chose to show notifications with window controls")
        else:
            NotifierWidget().settings.setValue('frame', "False")
            self.instructions_label.setText(
                "Notifications will not have window controls")

    def nosound_setting(self, state):
        if state == Qt.Checked:
            NotifierWidget().settings.setValue('nosound', "True")
            self.instructions_label.setText(
                'You chose not to play any sound for incoming notifications')
        else:
            NotifierWidget().settings.setValue('nosound', "False")
            self.instructions_label.setText(
                'A sound will be played when you receive a notification')

    def orientation_change(self, index):
        NotifierWidget().settings.setValue('direction', self.orient_combo.itemText(index))
        self.instructions_label.setText("Notifications will be shown in the: " +
                                        NotifierWidget().settings.value('direction') + " part of your screen")

    def language_change(self, index):
        NotifierWidget().settings.setValue('language', self.lingua_combo.itemText(index))
        self.instructions_label.setText(
            "Notifications will be translated to: " + NotifierWidget().settings.value('language'))

    def size_setting(self, value):
        NotifierWidget().settings.setValue('size', value)
        self.instructions_label.setText(
            'Notications\'s width changed to: ' + str(self.sl.value()) + " pixels")

    def opacity_setting(self, index):
        NotifierWidget().settings.setValue(
            'opacity', float(self.opa_combo.itemText(index)))
        percent = int(float(self.opa_combo.itemText(index)) * 100)
        self.instructions_label.setText(
            'Opacity changed to: ' + str(percent) + "%")

    def duration_setting(self, index):
        NotifierWidget().settings.setValue(
            'duration', str(self.dura_combo.itemText(index)))
        self.instructions_label.setText(
            'Notifications will be shown for: ' + NotifierWidget().settings.value('duration') + ' second(s)')

    def reminderdelay_setting(self, time):
        value = self.remi_spin.time()
        diff = QTime(QTime(0, 0)).secsTo(self.remi_spin.time())
        NotifierWidget().settings.setValue('reminderTime', str(diff))
        minutes = int(diff / 60)
        if minutes < 60:
            self.instructions_label.setText('Reminder interval is: ' + str(
                minutes) + ' minutes from now' + " - add some reminder text to finish setting up your reminder")
        else:
            hourss = float(minutes / 60)
            hours = int(hourss)
            mins = hourss-floor(hourss)
            minutes = round(mins * 60)
            self.instructions_label.setText('Reminder interval is: ' + str(hours) + ' hour(s)' + " and " + str(
                minutes) + ' minutes from now' + "- add some reminder text to finish setting up your reminder")

    def remindertext_setting(self):
        NotifierWidget().settings.setValue('reminderText', self.ltedit.text())
        self.instructions_label.setText(
            'Reminder text: ' + str(NotifierWidget().settings.value('reminderText')) + " Reminder Activated")
        process = subprocess.Popen([self.ish, "-t", "Reminder", "-n", str(NotifierWidget().settings.value(
            'reminderText')), "--delay", NotifierWidget().settings.value('reminderTime')], shell=True, stdin=None, stdout=None,
            stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)

    def blocksenderapp_setting(self):
        if self.ltedit.text() != "" and self.ltedit.text() != " " and self.ltedit.text() != "  ":
            NotifierWidget().settings.setValue('blockedApp', self.ltedit.text())
            self.instructions_label.setText(
                "NotiPie will try its best not to send notifications from: " + str(NotifierWidget().settings.value('blockedApp')))


class NotifierWidget(QWidget):

    def __init__(self, parent=None):
        super(NotifierWidget, self).__init__()

        def get_script_dir(follow_symlinks=True):
            if getattr(sys, 'frozen', False):
                path = os.path.abspath(sys.executable)
            else:
                path = inspect.getabsfile(get_script_dir)
            if follow_symlinks:
                path = os.path.realpath(path)
            return path
        self.ish = str(get_script_dir())

        self.settings = QSettings(
            QDir.homePath() + r"\AppData\Roaming\Notipie\NotiPie.ini", QSettings.IniFormat)
        self.settings.setPath(QSettings.IniFormat, QSettings.UserScope,
                              r"\\AppData\Roaming\\Notipie\\NotiPie.ini")
        #self.sub = SettingsDialog()
        self.internet_access = self.have_internet()
        self.setObjectName("Notifier")

        screen = app.primaryScreen()
        rect = screen.availableGeometry()
        
        self.time = datetime.now()
        self.timestamp = datetime.now().strftime(" %H:%M - %d/%m")
        self.daystamp = datetime.now().strftime(" %d/%m/%Y")

        if 'linux' in sys.platform:
            if args.system or self.settings.value('service') == "True":
                os.system("notipie-listen --npath " + self.ish + " &")

        if not args.delay:
            self.setWindowTitle("NotiPie")
        else:
            self.setWindowTitle("NotiPie-Remind")
        self.setWindowIcon(qta.icon("ri.notification-3-line"))

        if args.opacity:
            self.setWindowOpacity(float(args.opacity))
        else:
            try:
                self.setWindowOpacity(float(self.settings.value('opacity')))
            except:
                self.setWindowOpacity(0.85)

        self.chosen_orient = self.settings.value('direction')

        if self.chosen_orient == "random":
            direction_list = ['north', 'ne', 'nw', 'south',
                              'se', 'sw', 'west', 'center', 'east']
            self.set_orient = random.choice(direction_list)
        elif self.chosen_orient == "maximized":
            self.set_orient = "maximized"
        elif self.chosen_orient == "none" or self.chosen_orient is None:
            self.set_orient = "north"
        else:
            self.set_orient = self.settings.value('direction')

        if args.maximized:
            self.arg_orient = "maximized"
        elif args.message:
            self.arg_orient = "message"
        else:
            if args.xy == "random":
                direction_list = ['north', 'ne', 'nw', 'south',
                                  'se', 'sw', 'west', 'center', 'east']
                self.arg_orient = random.choice(direction_list)
            else:
                self.arg_orient = args.xy

        if self.arg_orient:
            self.orientation = self.arg_orient
        elif self.arg_orient and self.set_orient:
            self.orientation = self.arg_orient
        else:
            self.orientation = self.set_orient

        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()

        if self.orientation == "maximized":
            if args.animated == "Yes":
                self.manim_resize = QPropertyAnimation(self, b"size")
                self.manim_resize.setStartValue(
                    QSize(int(rect.width()/2), int(rect.height()/2)))
                self.manim_resize.setEndValue(
                    QSize(rect.width(), rect.height()))
                self.manim_resize.setDuration(300)
            elif args.animated == "No":
                self.setGeometry(1, 1, rect.width(), rect.height())
            else:
                if self.settings.value('animation') == "True":
                    self.manim_resize = QPropertyAnimation(self, b"size")
                    self.manim_resize.setStartValue(
                        QSize(int(rect.width()/2), int(rect.height()/2)))
                    self.manim_resize.setEndValue(QSize(rect.size()))
                    self.manim_resize.setDuration(300)
                else:
                    self.setGeometry(1, 1, rect.width(), rect.height())

        self.set_size = self.settings.value('size')
        if args.size:
            prop_ratio = args.size / 100
            prop_width = round(int(rect.width()) * prop_ratio)
        elif self.set_size:
            prop_width = int(self.set_size)
        else:
            prop_width = int(rect.width()) * 0.315
        self.fixed_width = round(prop_width / 2) * 2

        if args.square or self.settings.value('squared') == "True" and not args.nosquare:
            self.fixed_height = self.fixed_width
        else:
            self.fixed_height = round(int(self.fixed_width) * 0.5625)

        if args.animated or self.settings.value('animation') == "True":
            self.anim = QPropertyAnimation(self, b"pos")
            self.anim.setEasingCurve(QEasingCurve.Linear)
            self.anim.setDuration(300)
            self.banim = QPropertyAnimation(self, b"pos")
            self.banim.setEasingCurve(QEasingCurve.OutBounce)
            self.banim.setDuration(300)
            if self.orientation == "nw":
                self.anim.setStartValue(
                    QPoint(int(rect.width()/2 - self.fixed_width / 2), 30))
                self.anim.setEndValue(QPoint(30, 30))
            elif self.orientation == "ne":
                self.anim.setStartValue(
                    QPoint(int(rect.width()/2 - self.fixed_width / 2 - 30), 30))
                self.anim.setEndValue(
                    QPoint(int(rect.width() - self.fixed_width - 30), 30))
            elif self.orientation == "sw":
                self.anim.setStartValue(QPoint(int(rect.width(
                )/2 - self.fixed_width / 2), int(rect.height()) - self.fixed_height - 30))
                self.anim.setEndValue(
                    QPoint(30, int(rect.height()) - self.fixed_height - 30))
            elif self.orientation == "se":
                self.anim.setStartValue(QPoint(int(rect.width(
                )/2 - self.fixed_width / 2), int(rect.height()) - self.fixed_height - 30))
                self.anim.setEndValue(QPoint(int(rect.width(
                )) - self.fixed_width - 30, int(rect.height()) - self.fixed_height - 30))
            elif self.orientation == "center":
                self.anim.setStartValue(
                    QPoint(int(rect.width()/2 - self.fixed_width / 2), 1))
                self.anim.setEndValue(QPoint(round(int(rect.width(
                )/2 - self.fixed_width/2)), round(int(rect.height()/2 - self.fixed_height/2))))
            elif args.message:
                self.banim.setEndValue(QPoint(round(int(rect.width(
                )/2 - self.fixed_width/2)), round(int(rect.height()/2 - self.fixed_height/2))))
            elif self.orientation == "south":
                self.anim.setStartValue(QPoint(round(int(rect.width(
                )/2 - self.fixed_width/2)), round(int(rect.height()/2 - self.fixed_height/2))))
                self.anim.setEndValue(QPoint(round(int(rect.width(
                )/2 - self.fixed_width/2)), round(int(rect.height() - self.fixed_height - 30))))
            elif self.orientation == "north":
                self.anim.setStartValue(QPoint(30, 30))
                self.anim.setEndValue(
                    QPoint(int(rect.width()/2 - self.fixed_width/2), 30))
            elif self.orientation == "west":
                self.anim.setStartValue(QPoint(30, 30))
                self.anim.setEndValue(
                    QPoint(30, int(rect.height()/2 - self.fixed_height/2)))
            elif self.orientation == "east":
                self.anim.setStartValue(
                    QPoint(int(rect.width() - self.fixed_width - 30), 1))
                self.anim.setEndValue(QPoint(int(rect.width(
                ) - self.fixed_width - 30), int(rect.height()/2 - self.fixed_height/2)))
            else:
                self.anim.setStartValue(
                    QPoint(int(rect.width() - self.fixed_width - 30), 30))
                self.anim.setEndValue(
                    QPoint(int(rect.width()/2 - self.fixed_width/2), 30))

        if args.animated == "Yes":
            if args.message:
                self.banim.start()
            elif self.orientation == "maximized":
                self.manim_resize.start()
            else:
                self.anim.start()
        elif args.animated == "No":
            pass
        elif self.settings.value('animation') == "True":
            if args.message:
                self.banim.start()
            elif self.orientation == "maximized":
                self.manim_resize.start()
            else:
                self.anim.start()
        else:
            pass

        self.app_text = (args.app)
        self.appTextLabel = QLabel(
            self.app_text) if self.app_text else QLabel('NotiPie')
        if self.settings.value('fontSize') and int(self.settings.value('fontSize')) < 10:
            self.appTextLabel.setFont(QFont(self.settings.value('font'), int(
                self.settings.value('fontSize')) + 2, QFont.Bold))
        else:
            self.appTextLabel.setFont(
                QFont(self.settings.value('font'), 10, QFont.Bold))
        self.appTextLabel.setTextFormat(Qt.RichText)
        self.appTextLabel.setOpenExternalLinks(True)
        self.appTextLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.appTextLabel.setWordWrap(True)

        self.title_text = (args.title)

        if args.lingua or self.settings.value('translate') == "True" and self.internet_access == True:
            if self.settings.value('translate') == "True":
                targetlocale = self.settings.value('language')
            else:
                targetlocale = args.lingua
            lingua = Translator()
            title_translation = lingua.translate(
                self.title_text, dest=targetlocale)
            defaultitle_translation = lingua.translate(
                'This is a Title', dest=targetlocale)
            self.trans_titletext = title_translation.text
            self.defaultrans_titletext = defaultitle_translation.text
            self.titleTextLabel = QLabel(
                self.trans_titletext) if self.title_text else QLabel(self.defaultrans_titletext)
        else:
            self.titleTextLabel = QLabel(
                self.title_text) if self.title_text else QLabel('This is a Title')
        if self.settings.value('fontSize') and int(self.settings.value('fontSize')) < 11:
            self.titleTextLabel.setFont(QFont(self.settings.value(
                'font'), int(self.settings.value('fontSize')) + 1, QFont.Bold))
        else:
            self.titleTextLabel.setFont(
                QFont(self.settings.value('font'), 10, QFont.Bold))
        self.titleTextLabel.setTextFormat(Qt.RichText)
        self.titleTextLabel.setOpenExternalLinks(True)
        self.titleTextLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.titleTextLabel.setWordWrap(True)

        self.notification_text = (args.notification)
        if args.lingua or self.settings.value('translate') == "True" and not args.settings and self.internet_access == True:
            if self.settings.value('translate') == "True":
                targetlocale = self.settings.value('language')
            else:
                targetlocale = args.lingua
            lingua = Translator()
            notification_translation = lingua.translate(
                self.notification_text, dest=targetlocale)
            defaultnotification_translation = lingua.translate(
                'This is a Notification', dest=targetlocale)
            self.trans_notificationtext = notification_translation.text
            self.defaultrans_notificationtext = defaultnotification_translation.text
            self.notificationTextLabel = QLabel(
                self.trans_notificationtext) if self.notification_text else QLabel(self.defaultrans_notificationtext)
        else:
            quote = Quote.print(True)
            self.notificationTextLabel = QLabel(
                self.notification_text) if self.notification_text else QLabel(quote)

        try:
            self.notificationTextLabel.setFont(
                QFont(self.settings.value('font'), int(self.settings.value('fontSize'))))
        except:
            self.notificationTextLabel.setFont(
                QFont(self.settings.value('font'), 11))
        self.notificationTextLabel.setTextFormat(Qt.RichText)
        self.notificationTextLabel.setOpenExternalLinks(True)
        self.notificationTextLabel.setWordWrap(True)
        self.notificationTextLabel.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.notificationTextLabel.setFrameShape(QFrame.WinPanel)
        self.notificationTextLabel.setFrameShadow(QFrame.Raised)
        self.notificationTextLabel.setLineWidth(3)
        self.notificationTextLabel.setMidLineWidth(3)
        # self.notificationTextLabel.setAutoFillBackground(True)

        self.aBtn = QPushButton()
        self.aBtn.clicked.connect(self.run_command)

        if args.icon:
            self.aBtn.setIcon(qta.icon(f"{args.icon}"))
        else:
            self.aBtn.setIcon(qta.icon("msc.run-all"))

        self.aBtn.setIconSize(QSize(26, 26))
        self.aBtn.setText(args.button)
        self.aBtn.setShortcut(QKeySequence('X'))

        self.bBtn = QPushButton()

        if args.settings:
            self.bBtn.clicked.connect(self.show_settings)
        elif args.interact:
            self.bBtn.clicked.connect(self.inter_prompt)
        else:
            self.bBtn.clicked.connect(self.run_code)

        if args.icon2:
            self.bBtn.setIcon(qta.icon(f"{args.icon2}"))
        else:
            self.bBtn.setIcon(qta.icon("mdi.magnify"))

        self.bBtn.setIconSize(QSize(26, 26))
        self.bBtn.setText(args.button2)
        self.bBtn.setShortcut(QKeySequence('R'))

        self.closeBtn = QPushButton()
        self.closeBtn.clicked.connect(self.kill)

        if not args.appicon:
            self.closeBtn.setIcon(qta.icon("mdi.eye-off"))
        else:
            self.closeBtn.setIcon(QIcon.fromTheme(args.appicon))

        self.closeBtn.setIconSize(QSize(26, 26))
        self.closeBtn.setShortcut(QKeySequence('Q'))
        self.closeBtn.setToolTip('Dismiss me: (Q) or (Esc)')

        self.ledit = QLineEdit()
        self.ledit.setPlaceholderText("write here..")

        self.ledit.setClearButtonEnabled(True)
        if args.ex:
            self.ledit.setEchoMode(QLineEdit.Password)
        self.lay = QHBoxLayout()
        self.lay.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.lay.addWidget(self.appTextLabel)
        self.lay.addStretch()

        if args.framed:
            pass
        elif args.noframe:
            self.lay.addWidget(self.closeBtn)
        elif self.settings.value('frame') == "True":
            pass
        else:
            self.lay.addWidget(self.closeBtn)

        self.lay.setContentsMargins(5, 5, 5, 5)
        self.topbar = QWidget()
        self.topbar.setLayout(self.lay)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.topbar)
        if not args.viewlog:
            self.layout.addWidget(self.titleTextLabel)
            self.layout.addWidget(self.notificationTextLabel)
        else:
            self.historylog = QTextEdit()
            self.layout.addWidget(self.historylog)
            self.historylog.setHtml(self.get_html())
            self.historylog.scrollToAnchor(self.daystamp)

        if args.textline:
            self.layout.addWidget(self.ledit)
            self.ledit.setFocus(True)
        if args.tooltip:
            self.customtip = str(args.tooltip)
            self.aBtn.setToolTip(self.customtip + '> shortcut : X')
        else:
            self.customtip = "run"
            self.aBtn.setToolTip('run command > shortcut : X')
        if args.secondbutton or args.settings:
            self.layin = QHBoxLayout()
            self.layin.setAlignment(Qt.AlignTop | Qt.AlignRight)
            self.layin.addWidget(self.aBtn)
            self.layin.addStretch()
            self.layin.addWidget(self.bBtn)
            self.layin.setContentsMargins(5, 5, 5, 5)
            self.buttonbar = QWidget()
            self.buttonbar.setLayout(self.layin)
            self.layout.addWidget(self.buttonbar)
        else:
            self.layin = QHBoxLayout()
            self.layin.setAlignment(Qt.AlignTop | Qt.AlignRight)
            self.layin.addStretch()
            self.layin.addWidget(self.aBtn)
            self.layin.setContentsMargins(5, 5, 5, 5)
            self.buttonbar = QWidget()
            self.buttonbar.setLayout(self.layin)
            self.layout.addWidget(self.buttonbar)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        # Options to define positioning of notifications
        width = self.fixed_width
        if self.orientation == "maximized" or args.viewlog:
            self.setGeometry(1, 1, rect.width(), rect.height())
        elif self.orientation == "nw":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(30, 30, width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(30, 30, self.fixed_width, height)
        elif self.orientation == "ne":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(
                    int(rect.width()) - self.window().width() - 30, 30, self.fixed_width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(
                    int(rect.width()) - self.window().width() - 30, 30, self.fixed_width, height)
        elif self.orientation == "se":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(int(rect.width()) - self.window().width() - 30,
                                 int(rect.height()) - self.window().height() - 30, width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(int(rect.width()) - self.window().width() - 30,
                                 int(rect.height()) - height - 30, self.fixed_width, height)
        elif self.orientation == "sw":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(30, int(rect.height()) -
                                 self.window().height() - 30, width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(30, int(rect.height()) -
                                 height - 30, self.fixed_width, height)
        elif self.orientation == "center":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(int(rect.width()/2 - self.window().width()/2),
                                 int(rect.height()/2 - self.window().height()/2), width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(int(rect.width()/2 - self.window().width()/2),
                                 int(rect.height()/2) - int(height / 2), self.fixed_width, height)
        elif self.orientation == "south":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(int(rect.width()/2 - self.window().width()/2),
                                 int(rect.height() - self.window().height()) - 30, width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(int(rect.width()/2 - self.window().width()/2),
                                 int(rect.height()) - height - 30, self.fixed_width, height)
        elif self.orientation == "west":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(
                    30, int(rect.height()/2 - self.window().height()/2), width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(30, int(rect.height()/2) -
                                 int(height / 2), self.fixed_width, height)
        elif self.orientation == "east":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(int(rect.width()) - self.window().width() - 30,
                                 int(rect.height()/2 - self.window().height()/2), width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(int(rect.width()) - self.window().width() - 30,
                                 int(rect.height()/2) - int(height / 2), self.fixed_width, height)
        elif self.orientation == "north":
            if args.size:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = width
                else:
                    height = round(int(width) * 0.5625)
                self.setFixedWidth(width)
                self.setFixedHeight(height)
                self.setGeometry(
                    int(rect.width()/2 - self.window().width()/2), 30, width, height)
            else:
                if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                    height = self.fixed_width
                else:
                    height = round(int(self.fixed_width) * 0.5625)
                self.setFixedWidth(self.fixed_width)
                self.setGeometry(
                    int(rect.width()/2 - self.window().width()/2), 30, self.fixed_width, height)
        elif args.size and self.orientation == "Default (north)":
            if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                height = width
            else:
                height = round(int(width) * 0.5625)
            self.setFixedWidth(width)
            self.setFixedHeight(height)
            self.setGeometry(
                int(rect.width()/2 - self.window().width()/2), 30, width, height)
        else:
            width = self.fixed_width
            if args.square or self.settings.value('squared') == "True" and not args.nosquare:
                height = width
            else:
                height = round(int(width) * 0.5625)
            self.setFixedWidth(self.fixed_width)
            self.setFixedHeight(height)
            self.setGeometry(
                int(rect.width()/2 - self.window().width()/2), 30, width, height)

        self.setAutoFillBackground(True)

        if args.color:
            if args.color == "random":
                hex = "#"+''.join([random.choice('ABCDEF0123456789')
                                  for i in range(6)])
                self.color = str(hex)
            else:
                self.color = args.color
        else:
            if self.settings.value('randomcolor') == "True":
                hex = "#"+''.join([random.choice('ABCDEF0123456789')
                                  for i in range(6)])
                self.color = str(hex)
            else:
                self.color = self.settings.value('color')

        pal = QPalette()
        maincolor = QColor(self.color)
        pal.setColor(QPalette.Window, maincolor)
        self.setPalette(pal)
        radius = 7.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        self.mask = QRegion(path.toFillPolygon().toPolygon())

        if args.textcolor:
            self.tcolor = args.textcolor
        else:
            windowcolor = self.color
            self.tcolor = MostReadableColor.find_it(windowcolor)
        self.notificationTextLabel.setStyleSheet(
            "QLabel { color: "+self.tcolor+"; }")
        self.titleTextLabel.setStyleSheet("QLabel { color: "+self.tcolor+"; }")
        windowcolor = self.color
        self.acolor = MostReadableColor.find_it(windowcolor)
        self.appTextLabel.setStyleSheet("QLabel { color: "+self.acolor+"; }")

        if args.framed:
            self.isWindow()
            self.setWindowFlags(
                Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowSystemMenuHint)
        elif self.settings.value('frame') == "True" and not args.noframe:
            self.isWindow()
            self.setWindowFlags(
                Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint |
                                Qt.WindowStaysOnTopHint)

        if args.framed or self.settings.value('frame') == "True":
            pass
        else:
            self.setMask(self.mask)

        if not args.nolog and not self.settings.value('log') == "False" and not args.settings:
            if args.lingua or self.settings.value('translate') == "True" and self.internet_access == True:
                notification_logitem = "<pre></br><i>* At " + self.timestamp + " : </i></br><b>" + str(self.app_text) + "</b>" + " | " + str(
                    self.trans_titletext) + "</b>" + " | " + str(self.trans_notificationtext) + " </br><pre><a name=\"" + self.daystamp + "\" href=\"#\"></a><pre>"
            else:
                notification_logitem = "<pre></br><i>* At " + self.timestamp + " : </i></br><b>" + str(self.app_text) + "</b>" + " | " + str(
                    self.title_text) + "</b>" + " | " + str(self.notificationTextLabel.text()) + " </br><pre><a name=\"" + self.daystamp + "\" href=\"#\"></a><pre>"

            with open(QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-log.html", 'a', encoding="utf-8") as f:
                f.write(notification_logitem)

        if not args.nospoken and not args.settings and self.internet_access == True:
            if args.lingua or self.settings.value('translate') == "True" and self.internet_access == True:
                self.notification_spokenitem = str(self.app_text) + " \n\n " + str(
                    self.trans_titletext) + " \n\n " + str(self.trans_notificationtext)
            else:
                self.notification_spokenitem = str(self.app_text) + " \n\n " + str(
                    self.title_text) + " \n\n " + str(self.notificationTextLabel.text())
            with open(QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-speak.txt", 'w', encoding="utf8", errors='ignore') as f:
                f.write(self.notification_spokenitem)

        if args.clearlog:
            self.clear_logs()

        if args.spoken or self.settings.value('spoken') == "True" and not args.nospoken and not args.settings and self.internet_access == True:
            self.read_aloud()

        if args.hookfile:
            self.write_hook()

    def inter_prompt(self):
        pas = self.ledit.text()
        command = args.ex

        with subprocess.Popen(command.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8') as process:
            process.communicate(pas)
            process.wait()

    def write_hook(self):
        if args.hookfile and (args.hookcontent is None):
            parser.error(
                "--hookfile requires --hookcontent at least as empty argument, exiting..")
        with open(args.hookfile, 'w') as f:
            f.write(args.hookcontent)

    def history_view(self):
        try:
            self.close()
        except:
            pass
        process = subprocess.Popen([self.ish, "-a", "NotiPie", "-t", "Notification History", "-n", "Viewed", "-x", "notipie.py --duration 0 -i mdi6.progress-wrench --clearlog",
                                   "--delay", "1", "--tooltip", "Clear history", "-i", "msc.clear-all", "--viewlog", "--maximized", "--duration", "600"], shell=True, stdin=None, stdout=None,
                                   stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)

    def read_aloud(self):
        self.tts_convert()

    def show_about(self):
        try:
            self.timer.stop()
        except:
            pass
        try:
            self.tray_timer.stop()
        except:
            pass
        try:
            self.hide()
        except:
            pass
        self.aboutapp = QWidget()
        label1 = QLabel(self)
        label2 = QLabel(self)
        label3 = QLabel(self)
        label4 = QLabel(self)
        label5 = QLabel(self)
        self.pushButton = QPushButton(' MORE ')
        self.donateButton = QPushButton('DONATE')
        maintext = "NotiPie app empowers you as a user to customize incoming notifications \nor enables you as a developer to dispatch useful notifications and messages to your users or request user input and interaction. \nNotiPie is a default application in TeLOS Linux."
        label1.setText(maintext)
        label1.setContentsMargins(10, 10, 10, 10)
        label1.setStyleSheet("font-weight: bold; color: magenta")
        label1.setWordWrap(True)
        label1.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.cyan)
        label1.setPalette(palette)
        label1.setAlignment(Qt.AlignCenter)
        label2.setText(
            "\n© 2023 made with ♥ by Ion @TeLOS \nLicensed under GNU GPLv3 \n")
        label3.setAlignment(Qt.AlignCenter)
        label3.setToolTip('NotiPie\'s Logo')
        label3.setAlignment(Qt.AlignCenter)
        label3.setPixmap(qta.icon("mdi.chart-pie").pixmap(64, 64))
        sourcelink = "<a href='https://github.com/iontelos/notipie'>source code</a>"
        label4.setOpenExternalLinks(True)
        label4.setText(sourcelink)
        label4.setAlignment(Qt.AlignLeft)
        label4.setToolTip('inspect source - contribute')
        label5.setOpenExternalLinks(True)
        label5.setAlignment(Qt.AlignRight)
        label5.setText(
            "<a href='mailto:teloslinux@protonmail.com'>Contact</a>")
        label5.setToolTip('teloslinux@protonmail.com')

        self.pushButton.setIcon(qta.icon('fa5s.book-reader'))
        self.pushButton.clicked.connect(self.more_button)

        self.donateButton.setIcon(qta.icon('fa5s.donate'))
        self.donateButton.clicked.connect(self.donate_button)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        footerbox = QHBoxLayout()

        vbox.addWidget(label1)
        vbox.addWidget(label2)
        vbox.addWidget(label3)
        hbox.addWidget(self.pushButton)
        hbox.addWidget(self.donateButton)
        footerbox.addWidget(label4)
        footerbox.addWidget(label5)
        vbox.addLayout(hbox)
        vbox.addLayout(footerbox)

        label4.linkHovered.connect(self.linkHovered)
        label5.linkActivated.connect(self.linkClicked)
        self.aboutapp.setLayout(vbox)
        self.aboutapp.setWindowTitle('about NotiPie..')
        self.aboutapp.setWindowIcon(qta.icon("mdi.chart-pie"))
        self.aboutapp.show()

    def linkHovered(self):
        webbrowser.open("https://buymeacoffee.com")

    def linkClicked(self):
        webbrowser.open("https://github.com/iontelos/notipie")

    def more_button(self):
        webbrowser.open("https://teloslinux.org")
        self.pushButton.hide()

    def donate_button(self):
        webbrowser.open("https://buymeacoffee.com")
        self.donateButton.hide()

    def show_reminder(self):
        self.play_sound()
        self.setWindowFlags(Qt.CustomizeWindowHint)
        super().showNormal()
        self.unfade()

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        stickyAct = contextMenu.addAction("&Make sticky")
        stickyAct.setIcon(qta.icon("ph.sticker-bold"))
        readAct = contextMenu.addAction("&Read aloud")
        readAct.setIcon(qta.icon("mdi6.account-voice"))
        openAct = contextMenu.addAction("&Open log")
        openAct.setIcon(qta.icon("fa.history"))
        self.howlongago = self.relative_time(self.time)
        when = "Shown: " + self.howlongago
        timeAct = contextMenu.addAction(when)
        timeAct.setIcon(qta.icon("ei.time-alt"))
        testAct = contextMenu.addAction("&Test me")
        testAct.setIcon(qta.icon("ph.test-tube-fill"))
        setAct = contextMenu.addAction("&Settings")
        setAct.setIcon(qta.icon("mdi.cog"))
        if 'linux' in sys.platform:
            if os.path.isfile("/tmp/notipie-listen.lock"):
                serviceAct = contextMenu.addAction("&Pause service")
                serviceAct.setIcon(qta.icon("ph.pause-fill"))
            else:
                serviceAct = contextMenu.addAction("&Activate service")
                serviceAct.setIcon(
                    qta.icon("fa5s.assistive-listening-systems"))
        else:
            self.servactive = self.service_active()
            if self.servactive == True:
                serviceAct = contextMenu.addAction("&Pause service")
                serviceAct.setIcon(qta.icon("ph.pause-fill"))
            else:
                serviceAct = contextMenu.addAction("&Activate service")
                serviceAct.setIcon(
                    qta.icon("fa5s.assistive-listening-systems"))
        contextMenu.addSeparator()
        aboutAct = contextMenu.addAction("&Info")
        aboutAct.setIcon(qta.icon("mdi.help"))
        contextMenu.addSeparator()
        clearAct = contextMenu.addAction("&Clear logs")
        clearAct.setIcon(qta.icon("msc.clear-all"))
        quitAct = contextMenu.addAction("&Hide")
        quitAct.setIcon(qta.icon("mdi.notification-clear-all"))
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            self.kill()
        if action == stickyAct:
            self.timer.stop()
        if action == readAct:
            self.timer.stop()
            self.read_aloud()
        if action == clearAct:
            self.clear_logs()
        if action == testAct:
            self.send_test()
        if action == aboutAct:
            self.timer.stop()
            self.show_about()
        if action == openAct:
            super().showMinimized()
            self.history_view()
        if action == setAct:
            self.show_settings()
        if action == serviceAct:
            if 'linux' in sys.platform:
                if os.path.isfile("/tmp/notipie-listen.lock"):
                    os.system(
                        "rm /tmp/notipie-listen.lock && notipie-listen --quit &")
                    self.settings.setValue('service', "False")
                else:
                    os.system("notipie-listen --npath " + self.ish + " &")
                    self.settings.setValue('service', "True")
            else:
                self.servactive = self.service_active()
                if self.servactive == True:
                    self.kill_server()
                else:
                    self.activate_server()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            app.quit()

        return super().keyPressEvent(e)

    def get_html(self):
        historyfile = QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-log.html"
        html = ""
        with open(historyfile, "r", encoding="utf8", errors='ignore') as f:
            html = f.read()
        return html

    def run_command(self):
        if args.textline and args.command:
            argtext = str(self.ledit.text())
            command = args.command + " " + argtext
            os.system(command)
        elif args.command:
            command = args.command
            os.system(command)
        elif args.buttonlink:
            webbrowser.open(args.buttonlink)
        else:
            historyfile = QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-log.html"
            webbrowser.open(historyfile)

        if not args.sticky:
            self.kill

    def run_code(self):
        if args.textline and args.command2:
            argtext2 = str(self.ledit.text())
            command2 = args.command2 + " " + argtext2
            os.system(command2)
        elif args.command2:
            command2 = args.command2
            os.system(command2)
        elif args.buttonlink2:
            webbrowser.open(args.buttonlink)
        else:
            historyfile = QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-log.html"
            webbrowser.open(str(historyfile))

        if not args.sticky:
            self.kill

    def tts_convert(self):
        with open(QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-speak.txt", 'r', errors='ignore') as f:
            text = f.read()
            file = text

        dt = datetime.now()
        c_dtime = str(dt.strftime("%Y%m%d%H%M%S"))
        savepath = r"C:\Windows\Temp"
        ttsfile = savepath + "\\notipie_TTS_"+c_dtime+".mp3"
        returned_lang = detect(text)
        speech = gTTS(text=str(file), lang=str(returned_lang))
        speech.save(ttsfile)
        playsound(ttsfile)

    def have_internet(self) -> bool:
        conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            conn.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def show(self):
        if args.delay:
            self.dtimer = QTimer()
            reminder = int(args.delay) * 1000
            self.dtimer.timeout.connect(self.show_reminder)
            self.dtimer.setSingleShot(True)
            self.dtimer.start(reminder)
            # TODO add a settings' option to cancel reminder (self.dtimer.stop())
        else:
            QTimer.singleShot(50, self.play_sound)
            super().show()
            self.unfade()

    def clear_logs(self):
        historyfile = QDir.homePath() + r"\AppData\Roaming\Notipie\notipie-log.html"
        with open(historyfile, 'r+') as historyfileclear:
            historyfileclear.truncate(0)
        process = subprocess.run(
            [self.ish, "-t", "Success !", "-n", "Notifications cleared"], shell=True, stdin=None, stdout=None,
            stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)
        self.kill()

    def show_settings(self):
        try:
            self.timer.stop()
        except:
            pass
        try:
            self.tray_timer.stop()
        except:
            pass
        self.sub = SettingsDialog()
        self.sub.showMaximized()
        try:
            super().showMinimized()
        except:
            pass

    def send_test(self):
        process = subprocess.Popen([self.ish, "-a", "NotiPie", "-t", "Enjoy !", "-n",
                                   "This is a test notification", "--xy", "random", "-c", "random", "--animated", "--sticky"], shell=True, stdin=None, stdout=None,
                                   stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)

    def play_sound(self):
        if args.sticky or args.message:
            duration = 100000000
        elif args.duration:
            duration = int(args.duration) * 1000
        else:
            try:
                duration = int(self.settings.value('duration')) * 1000
            except:
                duration = 7000

        nonegative = duration - 2000
        if nonegative > 0:
            fadelay = nonegative
        else:
            fadelay = 500

        QTimer.singleShot(fadelay, self.fade)
        self.timer = QTimer()
        self.timer.timeout.connect(self.kill)
        self.timer.setSingleShot(True)
        self.timer.start(duration)

        if args.nosound and args.sound:
            parser.error(
                "-- not possible to play a sound with --nosound chosen, you requested an impossible combination, exiting..")
        if args.nosound:
            pass
        elif args.sound:
            not_sound = args.sound
            playsound(not_sound)
        else:
            if self.settings.value('nosound') == "True":
                pass
            elif self.settings.value('nosound') == "False":
                chosen_sound = self.settings.value('soundfile')
                if self.settings.value('soundfile') != "":
                    not_sound = chosen_sound
                else:
                    if getattr(sys, 'frozen', False):
                        not_sound = os.path.dirname(
                            os.path.realpath(sys.executable)) + "/not_sound.wav"
                    else:
                        not_sound = os.path.dirname(
                            os.path.realpath(sys.argv[0])) + "/not_sound.wav"
                    playsound(not_sound)

    def activate_server(self):
        if 'linux' in sys.platform:
            os.system("notipie-listen --npath " + self.ish + " &")
        else:
            destination = os.path.expandvars(
                '%APPDATA%\\Notipie\\notipie-listen.exe')
            nlpath = str(Path(destination))
            sprocess = subprocess.Popen([nlpath], shell=True,
                                        stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)
        self.settings.setValue('service', "True")

    def kill_server(self):
        if 'linux' in sys.platform:
            os.system("rm /tmp/notipie-listen.lock && notipie-listen --quit &")
        else:
            kprocess = subprocess.Popen(
                ["taskkill", "/im", "notipie-listen.exe", "/f"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)
        self.settings.setValue('service', "False")

    def whatsapp(self):
        if 'linux' in sys.platform:
            os.system("notipie-listen --whatsapp &")
        else:
            destination = os.path.expandvars(
                '%APPDATA%\\Notipie\\notipie-listen.exe')
            nlpath = str(Path(destination))
            sprocess = subprocess.Popen([nlpath, "--whatsapp"], shell=True,
                                        stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)
        self.settings.setValue('service', "True")

    def fade(self):
        self.feffect = QGraphicsOpacityEffect()
        self.appTextLabel.setGraphicsEffect(self.feffect)
        self.fanimation = QPropertyAnimation(self.feffect, b"opacity")
        self.fanimation.setDuration(1500)
        self.fanimation.setStartValue(1)
        self.fanimation.setEndValue(0.3)
        self.fanimation.start()

    def unfade(self):
        self.effect = QGraphicsOpacityEffect()
        self.notificationTextLabel.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1500)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1)
        self.animation.start()

    def relative_time(self, date):

        def formatn(n, s):
            """Add "s" if it's plural"""

            if n == 1:
                return "1 %s" % s
            elif n > 1:
                return "%d %ss" % (n, s)

        def qnr(a, b):
            """Return quotient and remaining"""

            return a / b, a % b

        class FormatDelta:

            def __init__(self, dt):
                now = datetime.now()
                delta = now - dt
                self.day = delta.days
                self.second = delta.seconds
                self.year, self.day = qnr(self.day, 365)
                self.month, self.day = qnr(self.day, 30)
                self.hour, self.second = qnr(self.second, 3600)
                self.minute, self.second = qnr(self.second, 60)

            def format(self):
                for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                    n = getattr(self, period)
                    if n >= 1:
                        return '{0} ago'.format(formatn(n, period))
                return "just now"

        return FormatDelta(date).format()

    def service_active(self):
        if "notipie-listen.exe" in (p.name() for p in psutil.process_iter()):
            return True
        else:
            return False

    def kill(self):
        self.hide()
        self.sys_tray()
        self.tray_timer = QTimer()
        self.tray_timer.setSingleShot(True)
        self.tray_timer.timeout.connect(app.quit)
        # TODO implement a worker here for long running task
        self.tray_timer.start(600000)

    def kill_all(self):
        process = subprocess.Popen(["pkill", "-f", "notipie.py"])

    def quit_all(self):
        atexit.register(self.terminate)
        sys.exit(0)

    def terminate(self):
        kprocess = subprocess.Popen(
            ["taskkill", "/im", "notipie.exe", "/f"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=CREATE_NO_WINDOW)
        sys.exit(0)

    def sys_tray(self):
        self.tray = QSystemTrayIcon()
        self.trayicon = QIcon(qta.icon("mdi.chart-pie").pixmap(22, 22))
        self.tray.setIcon(self.trayicon)
        self.tray.setToolTip("NotiPie")

        self.traymenu = QMenu(parent=None)

        self.restore_action = QAction("&Restore")
        self.restore_action.setIcon(qta.icon("mdi.backup-restore"))
        self.restore_action.triggered.connect(self.show)
        self.traymenu.addAction(self.restore_action)
        self.openlog_action = QAction("&Open log")
        self.openlog_action.setIcon(qta.icon("fa.history"))
        self.openlog_action.triggered.connect(self.history_view)
        self.traymenu.addAction(self.openlog_action)
        self.settings_action = QAction("&Settings")
        self.settings_action.setIcon(qta.icon("fa.cog"))
        self.settings_action.triggered.connect(self.show_settings)
        self.traymenu.addAction(self.settings_action)
        self.test_action = QAction("&Test me!")
        self.test_action.setIcon(qta.icon("ph.test-tube-fill"))
        self.test_action.triggered.connect(self.send_test)
        self.traymenu.addAction(self.test_action)
        self.start_action = QAction("&Activate Service")
        self.start_action.setIcon(qta.icon("ri.notification-3-line"))
        self.start_action.triggered.connect(self.activate_server)
        self.stop_action = QAction("&Pause Service")
        self.stop_action.setIcon(qta.icon("ph.pause-fill"))
        self.stop_action.triggered.connect(self.kill_server)
        if 'linux' in sys.platform:
            if os.path.isfile("/tmp/notipie-listen.lock"):
                self.traymenu.addAction(self.stop_action)
            else:
                self.traymenu.addAction(self.start_action)
        else:
            self.servactive = self.service_active()
            if self.servactive == True:
                self.traymenu.addAction(self.stop_action)
            else:
                self.traymenu.addAction(self.start_action)
        self.wa_action = QAction("&WhatsApp")
        self.wa_action.setIcon(qta.icon("mdi.whatsapp"))
        self.wa_action.triggered.connect(self.whatsapp)
        self.traymenu.addAction(self.wa_action)
        self.traymenu.addSeparator()
        self.about_action = QAction("&About NotiPie")
        self.about_action.setIcon(qta.icon("mdi.help"))
        self.about_action.triggered.connect(self.show_about)
        self.traymenu.addAction(self.about_action)
        self.traymenu.addSeparator()
        self.clear_action = QAction("&Clear History")
        self.clear_action.setIcon(qta.icon("mdi6.notification-clear-all"))
        self.clear_action.triggered.connect(self.clear_logs)
        self.traymenu.addAction(self.clear_action)
        self.quitall_action = QAction("Close al&l")
        self.quitall_action.setIcon(
            qta.icon("mdi6.close-box-multiple-outline"))
        if 'linux' in sys.platform:
            self.quitall_action.triggered.connect(self.kill_all)
        else:
            self.quitall_action.triggered.connect(self.quit_all)
        self.traymenu.addAction(self.quitall_action)
        self.quit_action = QAction("&Quit")
        self.quit_action.setIcon(qta.icon("mdi6.location-exit"))
        self.quit_action.triggered.connect(app.quit)
        self.traymenu.addAction(self.quit_action)
        self.tray.setContextMenu(self.traymenu)
        self.tray.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("NotiPie")
    app.setOrganizationName("TeLOS")
    app.setOrganizationDomain("https://teloslinux.org")

    parser = argparse.ArgumentParser(prog="notipie", description="NotiPie : Notifications, notification-handling service and more..",
                                     epilog="~~ Use NotiPie, customize NotiPie to your needs. Enjoy ! - read more-contribute : https://github.com/iontelos/notipie ~~")
    parser.add_argument('--settings', help='open graphical settings dialog (optional - hint: most graphical settings can be overriden when launching NotiPie from the command line, use the graphical settings to define an app to block its notifications)', default=False, action='store_true')
    parser.add_argument('--system', help='run notipie-listen in the background to show system notifications with NotiPie (optional - hint: you can keep your existing system notification app, possibly just deactivate it not to receive double notifications', default=False, action='store_true')
    parser.add_argument('-a', '--app', help='application sending the notification (optional)',
                        required=False, nargs='?', const='No app defined', default='NotiPie')
    parser.add_argument('-t', '--title', help='notification\'s title (optional)',
                        required=False, nargs='?', const='No title provided', default='This is a Title')
    parser.add_argument('-n', '--notification', help='notification\'s main text (optional)',
                        required=False, nargs='?', const='No text provided', default='')
    parser.add_argument('-w', '--xy', help='the position on your screen you want notifications to appear on (optional)', choices=[
                        'north', 'ne', 'east', 'se', 'south', 'sw', 'west', 'nw', 'center', 'maximized', 'random'], required=False, nargs='?', const='se', default='')
    parser.add_argument('-d', '--duration', help='notification\'s duration in seconds (optional)',
                        required=False, nargs='?', const=15, default='')
    parser.add_argument('-o', '--opacity', help='notifications\'s window opacity (optional - hint: choose a number from 0.30 to 1)',
                        required=False, nargs='?', const=0.7, default='')
    parser.add_argument('-sticky', '--sticky',
                        help='window will stay open until user closes it (optional)', default=False, action='store_true')
    parser.add_argument(
        '-delay', '--delay', help='show a notification after a given time in n seconds (optional - this is to use NotiPie as a reminders\' app)', nargs='?', const=900, default=0)
    parser.add_argument('-message', '--message',
                        help='show a message in the middle of the screen (optional - using this option will override any --xy argument)', default=False, action='store_true')
    parser.add_argument('-maximized', '--maximized',
                        help='show maximum size screen notifications - also configurable from argument --xy as a suboption (optional - don\'t use this together with --settings option)', default=False, action='store_true')
    parser.add_argument('-appicon', '--appicon',
                        help='app sender button icon, clicking the button with this icon will close the notification (optional - this is an icon from local system icon theme)', required=False)
    parser.add_argument('-s', '--sound', help='sound to play (optional - provide filepath to a .wav file)',
                        required=False, nargs='?', const=r"\AppData\Roaming\Notipie\not_sound.wav", default='')
    parser.add_argument('-nosound', '--nosound',
                        help='play no sound for incoming notifications', default=False, action='store_true')
    parser.add_argument('-c', '--color', help='notification\'s window background color (optional - provide a color\'s name in english or a color hex code in quotes)',
                        nargs='?', const='cyan', default='', required=False)
    parser.add_argument('-u', '--textcolor', help='choose text color (optional - provide a color\'s name in english or a color hex code in quotes)',
                        nargs='?', const='black', default='', required=False)
    parser.add_argument('-b', '--button', help='main button\'s text (optional - hint: main button is the button shown after the notification. When used together with --secondbutton option main button is the left lower one)',
                        nargs='?', const='Go', default='', required=False)
    parser.add_argument('-i', '--icon', help='main button\'s icon (optional - choose from qtawesome | pip install qtawesome or apt install python3-qtawesome python-qtawesome-common to use qta-browser command and browse all available icons)', required=False)
    parser.add_argument('-tooltip', '--tooltip',
                        help='main button\'s tooltip (optional)', required=False)
    parser.add_argument(
        '-x', '--command', help='command to execute on main button\'s click (optional)', required=False)
    parser.add_argument('-l', '--buttonlink',
                        help='main button\'s link (optional)', required=False)
    parser.add_argument('-animated', '--animated', help='show motion-animated notifications (optional - support is system-dependant)',
                        choices=['Yes', 'No'], required=False, nargs='?', const='Yes', default='')
    parser.add_argument('-z', '--size', help='window\'s width as percentage of the screen resolution\'s width (optional - provide a value in the range 25 - 80 and the window\'s height will be automatically calculated proportionally to your desired width with the exception of --square option | hint: use the -z without argument to show sligthly smaller notifications than the default)', nargs='?', type=int, choices=range(25, 81), const=28, required=False)
    groupA = parser.add_mutually_exclusive_group()
    groupA.add_argument('-q', '--square', help='show square-shaped notifications (optional)',
                        required=False, default=False, action='store_true')
    groupA.add_argument('-nosquare', '--nosquare',
                        help='use this option to override user-defined option to show square notifications ~DEV~ (optional)', default=False, action='store_true')
    groupB = parser.add_mutually_exclusive_group()
    groupB.add_argument('-framed', '--framed',
                        help='window\'s titlebar will be shown - notifications\' windows will be movable (optional)', default=False, action='store_true')
    groupB.add_argument('-noframe', '--noframe',
                        help='use this option to override user-defined option to show framed notifications ~DEV~ (optional)', default=False, action='store_true')
    groupC = parser.add_mutually_exclusive_group()
    groupC.add_argument('-spoken', '--spoken',
                        help='notifications will be read aloud with Google Text to Speech (optional - requires internet access)', default=False, action='store_true')
    groupC.add_argument('--nospoken', help='use this option to override user-defined option to read aloud incoming notifications ~DEV~ (optional)',
                        default=False, action='store_true')
    parser.add_argument('-lingua', '--lingua',
                        help='notifications will be translated to the language provided as argument with Google Translate (optional - requires internet access)', nargs='?', const='es', default='')
    parser.add_argument('-secondbutton', '--secondbutton',
                        help='add a second command button (optional)', default=False, action='store_true')
    parser.add_argument('-button2', '--button2', help='2nd button\'s text (optional)',
                        nargs='?', const='Go', default='', required=False)
    parser.add_argument(
        '-icon2', '--icon2', help='2nd button\'s icon (optional - choose from qtawesome)', required=False)
    parser.add_argument('-tooltip2', '--tooltip2',
                        help='2nd button\'s tooltip (optional)', required=False)
    parser.add_argument(
        '--command2', help='command to execute on 2nd button\'s click (optional)', required=False)
    parser.add_argument('-buttonlink2', '--buttonlink2',
                        help='2nd button\'s link (optional)', required=False)
    parser.add_argument('--textline', help='add a line to accept textual user input (optional)',
                        default=False, action='store_true')
    parser.add_argument('-viewlog', '--viewlog',
                        help='show notification logs (optional action)', default=False, action='store_true')
    parser.add_argument('-clearlog', '--clearlog',
                        help='clear notification history (optional action)', default=False, action='store_true')
    parser.add_argument('-nolog', '--nolog', help='NotiPie will not log her own notifications when launched with this argument',
                        default=False, action='store_true')
    parser.add_argument('-interact', '--interact',
                        help='interact with scripts ~DEV~ (optional)', default=False, action='store_true')
    parser.add_argument('-ex', '--ex', help='interactive mode command ~DEV~ (optional)',
                        required=False, action='store_true')
    parser.add_argument('-hookfile', '--hookfile', help='create a hookfile ~DEV~ (optional - provide user-writable path)',
                        type=str, nargs='?', const='notipie-hook.txt', required=False)
    parser.add_argument('-hookcontent', '--hookcontent', help='content to be written to the hookfile ~DEV~ (optional)',
                        type=str, nargs='?', const='This is a text hook', required=False)
    args = parser.parse_args()

    mainWin = NotifierWidget()
    settingsWin = SettingsDialog()

    if args.settings:
        settingsWin.show()
        sys.exit(app.exec_())
    elif args.clearlog:
        mainWin.clear_logs()
        sys.exit(app.exec_())

    try:
        blocked_app = mainWin.settings.value('blockedApp')
    except:
        pass

    text_tocheck = mainWin.app_text
    if text_tocheck.find(str(blocked_app)) != -1 and str(blocked_app) != "":
        sys.exit(0)
    elif not args.settings:
        mainWin.show()

    #app.setQuitOnLastWindowClosed(False)

    sys.exit(app.exec_())
