# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'baseball_interface.ui'
#
# Created: Wed Apr 24 01:41:25 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!


##########################################################################################
###### Possible for the button to trigger a new window that will stream download progress?
##########################################################################################
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
import download
import datetime
import time
import os
import sys

date = time.strftime("_%m_%d_%Y")
directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Data', date))

if not os.path.exists(directory):
    os.makedirs(directory)
f = open(directory+'/Log.txt', 'a')

sys.stdout = f
teams, overall, downloadedFiles = download.load_teams()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class Window(QtGui.QWidget):
    def __init__(self, buttontext, command):
        QtGui.QWidget.__init__(self)
        self.command = command
        layout = QtGui.QVBoxLayout(self)
        self.setWindowTitle(buttontext)
        self.textEdit = QtGui.QTextEdit()
        layout.addWidget(self.textEdit)
        if buttontext == 'Download Pollen':
            newPollen = QtGui.QPushButton('Updated data already')
            oldPollen = QtGui.QPushButton('No New Data')
            layout.addWidget(newPollen)
            layout.addWidget(oldPollen)
            newPollen.clicked.connect(self.handleTrue)
            oldPollen.clicked.connect(self.handleFalse)
        elif buttontext == 'Download Everything' or buttontext == 'Send a new email':
            zipEmail = QtGui.QPushButton('Download and Email Zip File')
            layout.addWidget(zipEmail)
            sumEmail = QtGui.QPushButton('Download and Email Summary File')
            layout.addWidget(sumEmail)
            noEmail = QtGui.QPushButton('Download and Don\'t Email')
            layout.addWidget(noEmail)
            zipEmail.clicked.connect(self.handleTrue)
            sumEmail.clicked.connect(self.handleAlt)
            noEmail.clicked.connect(self.handleFalse)
        else:
            downloadBtn = QtGui.QPushButton(buttontext)
            layout.addWidget(downloadBtn)
            downloadBtn.clicked.connect(self.handleFalse)

        #sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

    def handleTrue(self, command):
        import download
        self.normalOutputWritten('Started downloading {0}: {1}\n\n\n'.format(self.command, datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        teams, overall, downloadedFiles = download.load_teams()
        download.processGUI(self.command, teams, overall, downloadedFiles, True)

    def handleFalse(self, command):
        import download
        self.normalOutputWritten('Started downloading {0}: {1}\n\n\n'.format(self.command, datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        teams, overall, downloadedFiles = download.load_teams()
        download.processGUI(self.command, teams, overall, downloadedFiles, False)

    def handleAlt(self, command):
        import download
        self.normalOutputWritten('Started downloading Everything: {0}\n\n\n'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        teams, overall, downloadedFiles = download.load_teams()
        download.processGUI(self.command, teams, overall, downloadedFiles, 'email_sum')

    def normalOutputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("Download Baseball Data"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-10, -10, 811, 581))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))

        statsBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        statsBtn.setObjectName(_fromUtf8("statsBtn"))
        self.verticalLayout.addWidget(statsBtn)

        schedBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        schedBtn.setObjectName(_fromUtf8("schedBtn"))
        self.verticalLayout.addWidget(schedBtn)

        broadBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        broadBtn.setObjectName(_fromUtf8("broadBtn"))
        self.verticalLayout.addWidget(broadBtn)

        pollenBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        pollenBtn.setObjectName(_fromUtf8("pollenBtn"))
        self.verticalLayout.addWidget(pollenBtn)

        overallBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        overallBtn.setObjectName(_fromUtf8("overallBtn"))
        self.verticalLayout.addWidget(overallBtn)

        allBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        allBtn.setObjectName(_fromUtf8("allBtn"))
        self.verticalLayout.addWidget(allBtn)

        emailBtn = QtGui.QPushButton(self.verticalLayoutWidget)
        emailBtn.setObjectName(_fromUtf8("emailBtn"))
        self.verticalLayout.addWidget(emailBtn)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.action_Quit = QtGui.QAction(MainWindow)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.menu_File.addAction(self.action_Quit)
        self.menubar.addAction(self.menu_File.menuAction())

        overallBtn.setText(_translate("MainWindow", "Download Overall Data", None))
        statsBtn.setText(_translate("MainWindow", "Download Stats Data", None))
        schedBtn.setText(_translate("MainWindow", "Download Schedule Data", None))
        broadBtn.setText(_translate("MainWindow", "Download Broadcast Data", None))
        pollenBtn.setText(_translate("MainWindow", "Download Pollen Data", None))
        allBtn.setText(_translate("MainWindow", "Download Everything", None))
        emailBtn.setText(_translate("MainWindow", "Send a new email", None))
        self.retranslateUi(MainWindow)

        overallBtn.clicked.connect(self.overall)
        statsBtn.clicked.connect(self.stats)
        schedBtn.clicked.connect(self.schedule)
        broadBtn.clicked.connect(self.broadcast)
        pollenBtn.clicked.connect(self.pollen)
        allBtn.clicked.connect(self.downloadAll)
        emailBtn.clicked.connect(self.newEmail)

        QtCore.QObject.connect(self.action_Quit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Download Baseball Data", None))

        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.action_Quit.setText(_translate("MainWindow", "&Quit", None))

    def pollen(self):
        print("Opening a new popup window...")
        self.w = Window('Download Pollen', 'iterate_allergy')

        self.w.show()

    def stats(self):

        print("Opening a new popup window...")
        self.w = Window('Download Stats', 'iterate_stats')

        self.w.show()

    def broadcast(self):

        print("Opening a new popup window...")
        self.w = Window('Download Broadcast', 'iterate_broadcast')

        self.w.show()

    def schedule(self):

        print("Opening a new popup window...")
        self.w = Window('Download Schedule', 'iterate_schedules')

        self.w.show()

    def overall(self):
        print("Opening a new popup window...")
        self.w = Window('Download Overall', 'iterate_overall')

        self.w.show()

    def downloadAll(self):
        print("Opening a new popup window...")
        self.w = Window('Download Everything', 'iterate_all')
        self.w.show()

    def newEmail(self):
        print("Opening a new popup window...")
        self.w = Window('Send a new email', 'send_email')

        self.w.show()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()

    teams2 = dict(teams)

    for team in teams2.keys():
        directory = os.path.join('Data', date, 'Promo', team+date+".csv")
        if os.path.exists(directory):
            del teams[team]
            print("Already got it team {0}: url - {1}".format(team, teams2[team]['promo']))
    if teams:
        app.quit()
        from promo_interface import Downloader
        downloader = Downloader(sorted(list(teams.keys())), teams, f)
        downloader.done.connect(app.quit)
        web = QWebView()
        web.setPage(downloader.page)
        web.show()
    else:
        sys.exit()
    sys.stdout.flush()
    sys.stdout = sys.__stdout__
    f.close()

    sys.exit(app.exec_())
