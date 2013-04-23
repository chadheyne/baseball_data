#!/usr/bin/env python3

from bs4 import BeautifulSoup
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from collections import defaultdict, deque

import urllib
import urllib.request
import sys
import time
import csv
import os

NUM_THREADS = 2

class Render(QWebView):
	active = deque() # track how many threads are still active
	data = {} # store the data

	def __init__(self, urls):
		QWebView.__init__(self)
		self.loadFinished.connect(self._loadFinished)
		self.urls = urls
		self.crawl()

	def crawl(self):
		try:
			url = self.urls.pop()
			Render.active.append(1)
			self.load(QUrl(url))
		except IndexError:
			if not Render.active:
				self.close()

	def _loadFinished(self, result):
        # process the downloaded html
		frame = self.page().mainFrame()
		url = str(frame.url().toString())
		print(url)
		Render.data[url] = frame.toHtml()
		try:
			Render.active.popleft()
		except IndexError:
			self.crawl()


		self.crawl() # crawl next URL in the list


def download_stats(team, name):
	
	if not team['stats'].endswith('shtml'):
		return
	
	date = time.strftime("_%m_%d_%Y")	

	directory = os.path.join('Data', 'Stats', date)
	if not os.path.exists(directory):
		os.makedirs(directory)
	
	datafile = os.path.join(directory,name+date+".csv")
	
	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['stats']))
		return
	
	csvf = open(datafile, "w", encoding='utf-8', newline = '')
	
	stats = BeautifulSoup(urllib.request.urlopen(team['stats']))
	
	for table in stats.find_all('table'):
		for row in table.find_all('tr'):
			col = row.get_text().split('\n')
			csvf.write('| '.join(col))
			csvf.write('\n')
	
	csvf.close()


#Opponent table
def download_schedules(team, name):
	
	if not team['schedules'].endswith('shtml'):
		return
	
	date = time.strftime("_%m_%d_%Y")	

	directory = os.path.join('Data', 'Schedules', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['schedules']))
		return
	
	csvf = open(datafile, "w", encoding='utf-8', newline = '')

	schedules = BeautifulSoup(urllib.request.urlopen(team['schedules']))

	for table in schedules.find_all('table'):

		
		if 'cellspacing' in table.attrs:
			if not table.find('td').get_text() == 'Season Summary':
			
				header = list(set([head.get_text() for head in table.find_all('th')]))
				data = [entry.get_text().strip() for entry in table.find_all('td') if not entry.find_all('th') and 'colspan' not in entry.attrs]
				sets = [entry.get_text().strip() for entry in table.find_all('td') if not entry.find_all('th') and 'colspan' in entry.attrs]
				tuples = list(zip(header*(len(data)//6), data))
			
				for tup in tuples:
					csvf.write(', '.join(tup))
					csvf.write('\n')
			
			elif table.find('td').get_text() == 'Season Summary':
			
				for row in table.find_all('tr'):
					data = [entry.text.strip().replace(',', '') for entry in row.find_all('td')]
					csvf.write(', '.join(data))
					csvf.write('\n')

			else:
				print("Unable to process Table: {0} with attributes {1}".format(table.name, table.attrs))

		elif table.attrs['id'] == 'team_schedule':
			for row in table.find_all('tr'):
				data = row.text.split('\n')
				csvf.write('| '.join(data))
				csvf.write('\n')

	csvf.close()


#Fix
def download_broadcast(team, name):
	
	if not team['broadcast'].endswith(name.lower()):
		return
	
	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', 'Broadcast', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")
	
	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['broadcast']))
		return
	
	csvf = open(datafile, "w", encoding='utf-8', newline = '')

	broadcast = BeautifulSoup(urllib.request.urlopen(team['broadcast']))

	for table in broadcast.find_all('table'):
		header = table.find_all('th')
		headers = [th.text for th in header]
		rows = table.find_all('tr')
		csvf.write('| '.join(headers))
		csvf.write('\n')
		for tr in rows[1:]:
			col = tr.get_text().split('\n')
			csvf.write('| '.join(col))
			csvf.write('\n')
	csvf.close()

def download_allergy(team, name):
	if not team['allergy'].endswith('Enter'):
		return
	date = time.strftime("_%m_%d_%Y")
	print(team['allergy'])

	directory = os.path.join('Data', 'Allergy', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")
	
	csvf = open(datafile, "w", encoding='utf-8', newline = '')

	allergy = BeautifulSoup(urllib.request.urlopen(team['allergy']))
	today = allergy.find('img', alt="Today's Pollen Level")
	findUp = today.find_parent().find_parent().find_all('td')
	(today, tomorrow, nextDay, twoNext) = findUp
	
	#Get the days off of the img. Possible to find out what day tomorrow/today are based on day(next)-1?
	dayToday = today.find('img')['alt'].split(' ')[0]
	dayTom = tomorrow.find('img')['alt'].split(' ')[0]
	dayNext = nextDay.find('img')['alt'].split(' ')[0]
	dayTwonext = twoNext.find('img')['alt'].split(' ')[0]

	srcToday = today.find('img')['src']
	srcTom = tomorrow.find('img')['src']
	srcNext = nextDay.find('img')['src']
	srcTwonext = twoNext.find('img')['src']

def download_promo(team, name):
	
	if not team['promo']:
		return
	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', 'Promo', date)
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['promo']))
		return

	csvf = open(datafile, "w", encoding='utf-8', newline = '')
	
	promo = BeautifulSoup(team['html'])
	csvf.write(', '.join(['Time', 'Date', 'Opponent', 'link1', 'link2']))
	csvf.write('\n')
	for table in promo.find_all('table'):
		
		if 'class' not in table.attrs or not table['class'][0] == 'data_grid':
			continue

		for row in table.find_all('tr'):
			cols = row.find_all('td')
			
			if len(cols) < 1:
				continue
		
			timeofday = cols[0].find('br').get_text()
			date = cols[0].find('b').get_text()
			opponent = cols[1].get_text()
			hits = [timeofday, date, opponent]
		
			for url in cols[2].find_all('a'):
				hits.append(url.get_text())
		
			
			csvf.write(', '.join(hits))
			csvf.write('\n')
	time.sleep(42)
	csvf.close()
	return

def get_promos(teams):

	urls = deque([teams[team]['promo'] for team in teams.keys() if teams[team]['promo'] ])

	app = QApplication(sys.argv)

	renders = [Render(urls) for i in range(NUM_THREADS)]
	app.exec_()

	for team in teams:
		try:
			if not teams[team]['promo'] or not Render.data[teams[team]['promo']]:
				continue
		except KeyError:
			print(team, teams[team]['promo'])
			continue
		teams[team]['html'] = Render.data[teams[team]['promo']]

	return teams



if __name__ == "__main__":
	teams = defaultdict(dict)
	reader = csv.DictReader(open("Data/MLB 2013 Req Daily Info - Websites.csv"))
	for rows in reader:
		teams[rows['TEAM']] = {key.lower(): value.strip() for key, value in rows.items() if not key == 'TEAM'}
	
	#teams = get_promos(teams)
	
	for team in sorted(teams.keys()):
		if  team == 'ALL':
			continue
		#download_stats(links[team], team)
		#print('Downloading stats     for {0}: \t link: {1}'.format(team, teams[team]['stats']))
		#time.sleep(42)
		download_schedules(teams[team], team)
		print('Downloading schedules for {0}: \t link: {1}'.format(team, teams[team]['schedules']))
		
		#download_broadcast(teams[team], team)
		#print('Downloading broadcast for {0}: \t link: {1}'.format(team, teams[team]['broadcast']))
		#download_promo(teams[team], team)
		#print('Downloading promo     for {0}: \t link: {1}'.format(team, teams[team]['promo']))
		

# A6d = 12?			# 5Fm = 9
# A6c = 11			# 
# A6b = 10			# 60h = 7
# AE = 9			# 60g = 6
# AD = 8			# 60f = 5
# AC = 7			# 60e = 4
# AB = 6			# 5Fg = 3
# AA = 5			# 60c = 2 	
# A9 = 4			# 60b = 1
# A8 = 3			# 5Fd = 0 
# A7 = 2			#
# A6 = 1			#
# A5 = 0			#


# team = {}
# 		name = rows[0]
# 		team['broadcast'], team['promo'], team['stats'], team['schedules'], team['allergy'], team['standings'], team['wildcardStandings'] = rows[1:]
# 		teams[name] = team
# 	