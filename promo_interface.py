from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import sys
import codecs
import download
import time
import os

class Downloader(QObject):
	# To be emitted when every items are downloaded
	done = pyqtSignal()



	def __init__(self, urlList, teams, out = None, parent = None):
		super(Downloader, self).__init__(parent)
		self.urlList = urlList
		self.teams = teams
		if out:
			sys.stdout = out     
		# As you probably don't need to display the page
		# you can use QWebPage instead of QWebView
		self.page = QWebPage(self)      
		self.page.loadFinished.connect(self.save)
		self.currentTeam()

	def currentTeam(self):
		try:
			self.use =  self.urlList.pop()
			self.startNext()
		except IndexError:
			print("It looks like there's a problem!")
			self.done.emit()

	def startNext(self):
		
		self.page.mainFrame().load(QUrl(self.teams[self.use]['promo']))

	def save(self, ok):
		if ok:         
			data = self.page.mainFrame().toHtml()
			self.teams[self.use]['html'] = data
			
			results = download.download_promo(self.teams[self.use], self.use)
			print('Downloading promo     for {0}: \t link: {1}'.format(self.use, self.teams[self.use]['promo']))
		#else:
		#	print("Error while downloading %s\nSkipping."%self.currentUrl())
		if self.urlList:            
			self.currentTeam()
		else:

			self.done.emit()

app = QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()

teams, overall, downloadedFiles = download.load_teams()

for team in teams.keys():
	teams[team]['html'] = ''

date = time.strftime("_%m_%d_%Y")

teams2 = dict(teams)

for team in teams2.keys():
	directory = os.path.join('Data', date, 'Promo', team+date+".csv")
	if os.path.exists(directory):
		del teams[team]
		print("Already got it team {0}: url - {1}".format(team, teams2[team]['promo']))

downloader = Downloader(sorted(list(teams.keys())), teams)
downloader.done.connect(app.quit)
web = QWebView()
web.setPage(downloader.page)
web.show()

sys.exit(app.exec_())
