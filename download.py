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
			csvf.write(', '.join(col))
			csvf.write('\n')
	time.sleep(42)
	csvf.close()


def download_schedules(team, name):
	
	if not team['schedules'].endswith('shtml'):
		return
	
	date = time.strftime("_%m_%d_%Y")	

	directory = os.path.join('Data', 'Schedules', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['allergy']))
		return
	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	schedules = BeautifulSoup(urllib.request.urlopen(team['schedules']))

	for table in schedules.find_all('table'):

		
		if 'cellspacing' in table.attrs:
			if not table.find('td').get_text() == 'Season Summary':
			
				header = [head.get_text() for head in table.find_all('th')]
				headers = []
				[headers.append(item) for item in header if item not in headers]
				data = [entry.text.strip() for entry in table.find_all('td') if not entry.find_all('th') and 'colspan' not in entry.attrs]
				sets = [entry.text.strip() for entry in table.find_all('td') if not entry.find_all('th') and 'colspan' in entry.attrs]
				

				for i, split in enumerate(sets):
					csvf.writerow(['','',split]) #Get some extra padding at the front
					csvf.writerow(headers)
					csvf.writerow(data[i*6:i*6+6]) #There has to be a better way to zip this together. 
					

		#   update this so it prints to csv
			elif table.find('td').get_text() == 'Season Summary':
			
		 		for row in table.find_all('tr'):
		 			data = [entry.text.strip().replace(',', '') for entry in row.find_all('td')]
		 			csvf.writerow(data)
		 			
			else:
		 		print("Unable to process Table: {0} with attributes {1}".format(table.name, table.attrs))

		elif 'id' in table.attrs and table.attrs['id'] == 'team_schedule':
			headers = [item.text for item in table.find('tr').find_all('th')]
			csvf.writerow(headers)
			for row in table.find_all('tr'):
				data = [td.text for td in row.find_all('td') if not row.find('th')]
				csvf.writerow(data)

		else:
			print("Unable to process Table: {0} with attributes {1}".format(table.name, table.attrs))
	
	infile.close()
	time.sleep(42)
	return schedules


def download_broadcast(team, name):
	
	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', 'Broadcast', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")
	
	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['broadcast']))
		return
	
	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	broadcast = BeautifulSoup(urllib.request.urlopen(team['broadcast']))

	for table in broadcast.find_all('table'):

		rows = table.find('tr')
		headers = [th.text for th in rows if not th == '\n']
	
		csvf.writerow(headers)
		print(headers, name)
		for tr in rows.find_next_siblings():
			dateGame = tr.find('td')
			
			col = [c.text for c in dateGame.find_next_siblings()]
			col.insert(0, dateGame.text)
			radio = col.pop()
			col.extend(radio.split(', '))
			csvf.writerow(col)

	infile.close()
	return broadcast

def download_allergy(team, name, codes):

	if not team['allergy'].endswith('Enter'):
		return
	
	date = time.strftime("_%m_%d_%Y")
	
	#print(team['allergy'])

	directory = os.path.join('Data', 'Allergy', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['allergy']))
		return
	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	allergy = BeautifulSoup(urllib.request.urlopen(team['allergy']))

	data = allergy.find_all('td', class_="forecast-small-text")

	title1 = allergy.title.text.find('for ')
	title2 = allergy.title.text.find('| ')
	city = allergy.title.text[title1+3:title2].strip()

	#Get the days off of the img. Possible to find out what day tomorrow/today are based on day(next)-1?
	days = [day.text for day in data if not day.find('img')]
	imgs = [day.find('img')['src'].split('v=')[1] for day in data if day.find('img')]
	
	nums = [str(int(codes[i]['idx'])/10) for i in imgs if codes[i]['idx']]
	
	results = list(zip(days,nums))
	csvf.writerow(['City/Zip', 'Date'])
	csvf.writerow([city, date[1:]])
	csvf.writerows(results)

#Update this so it prints to csv
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

def get_allergycodes():

	allergy = defaultdict(dict)

	allergydata = csv.DictReader(open("Data/allergycodes.csv"))

	for row in allergydata:
		allergy[row['hexdigit']] = {key.lower(): value.strip() for key, value in row.items()}

	return allergy

def iterate_stats(teams):

	for team in sorted(teams.keys()):
		print('Downloading stats     for {0}: \t link: {1}'.format(team, teams[team]['stats']))

		download_stats(teams[team], team)

	return True

def iterate_schedules(teams):
	
	for team in sorted(teams.keys()):
		print('Downloading schedules     for {0}: \t link: {1}'.format(team, teams[team]['schedules']))

		download_schedules(teams[team], team)

	return True

#Some broadcasts don't download
#TBR, WSN, BAL, MIL
def iterate_broadcast(teams):

	for team in sorted(teams.keys()):
		print('Downloading broadcast     for {0}: \t link: {1}'.format(team, teams[team]['broadcast']))

		download_broadcast(teams[team], team)

	return True	

def iterate_promo(teams):

	teams = get_promos(teams)
	for team in sorted(teams.keys()):
		print('Downloading promo     for {0}: \t link: {1}'.format(team, teams[team]['promo']))

		download_promo(teams[team], team)

	return True

def iterate_allergy(teams):
	allergycodes = get_allergycodes()
	for team in sorted(teams.keys()):
		print('Downloading pollen     for {0}: \t link: {1}'.format(team, teams[team]['allergy']))

		download_allergy(teams[team], team, iterate_allergy)

	return True

def load_teams():
	teams = defaultdict(dict)
	teamdata = csv.DictReader(open("Data/MLB 2013 Req Daily Info - Websites.csv"))
	for rows in teamdata:
		teams[rows['TEAM']] = {key.lower(): value.strip() for key, value in rows.items() if not key == 'TEAM'} 
	overall = teams.pop('ALL')

	return teams, overall

def main():
	teams, overall = load_teams()
	#iterate_stats(teams)
	#iterate_schedules(teams)
	#iterate_promo(teams)
	#iterate_broadcast(teams)
	#iterate_allergy(teams)	
	return teams

if __name__ == "__main__":
	main()



