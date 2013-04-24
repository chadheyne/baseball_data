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
		return {'html': True, 'datafile': datafile}

	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)
	
	stats = BeautifulSoup(urllib.request.urlopen(team['stats']))
	
	for table in stats.find_all('table'):
		if 'id' in table.attrs:
			tableName = ' '.join(table.attrs['id'].split('_'))
		else:
			tableName = table.name
		header = [head.get_text() for head in table.find_all('th')]
		headers = []
		[headers.append(item) for item in header if item not in headers]
		csvf.writerow([tableName])
		csvf.writerow(headers)
		
		for row in table.find_all('tr'):
			data = [col.text for col in row.find_all('td')]
			csvf.writerow(data)
		
		csvf.writerow('\n')
	
	infile.close()
	time.sleep(42)
	
	return {'html': stats, 'datafile': datafile}

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
		return {'html': True, 'datafile': datafile}

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
	return {'html': schedules, 'datafile': datafile}


def download_broadcast(team, name):
	
	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', 'Broadcast', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")
	
	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['broadcast']))
		return {'html': True, 'datafile': datafile}
	
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
	return {'html': broadcast, 'datafile': datafile}

def download_allergy(team, name, codes):

	if not team['allergy'].endswith('Enter'):
		return
	
	date = time.strftime("_%m_%d_%Y")
	
	directory = os.path.join('Data', 'Allergy', date)
	
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['allergy']))
		return {'html': True, 'datafile': datafile, 'url': 'Already downloaded'}

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
	urls = ['www.pollen.com/' + day.find('img')['src'] for day in data if day.find('img')]
	#nums = [str(int(codes[i]['idx'])/10) for i in imgs if codes[i]['idx']]
	
	results = list(zip(days,imgs, urls))
	csvf.writerow(['City/Zip', 'Date'])
	csvf.writerow([city, date[1:]])
	csvf.writerows(results)
	return {'html': allergy, 'datafile': datafile, 'url': urls}

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
		return {'html': True, 'datafile': datafile}

	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	
	promo = BeautifulSoup(team['html'])
	csvf.writerow(['Time', 'Date', 'Opponent', 'Promotion', 'Links'])
	for table in promo.find_all('table'):
		
		if 'class' not in table.attrs or not table['class'][0] == 'data_grid':
			continue

		for row in table.find_all('tr'):
			cols = row.find_all('td')
			
			if len(cols) < 1:
				continue
		
			timeofday = cols[0].find('br').text
			date = cols[0].find('b').text
			opponent = cols[1].text
			hits = [timeofday, date, opponent]
		
			for url in cols[2].find_all('a'):
				hits.append(url.text)
		
			
			csvf.writerow(hits)
			
	infile.close()
	return {'html': promo, 'datafile': datafile}

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

def iterate_stats(teams, downloadedFiles):

	for team in sorted(teams.keys()):
		results = download_stats(teams[team], team)
		
		if results['html'] is True:
			continue

		print('Downloading stats     for {0}: \t link: {1}'.format(team, teams[team]['stats']))
		
		data = results['datafile']		
		downloadedFiles[team]['Stats'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

	return True

def iterate_schedules(teams, downloadedFiles):
	
	for team in sorted(teams.keys()):
		results = download_schedules(teams[team], team)
		
		if results['html'] is True:
			continue
		
		print('Downloading schedules     for {0}: \t link: {1}'.format(team, teams[team]['schedules']))
		
		data = results['datafile']
		downloadedFiles[team]['Schedules'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

	return True

#Some broadcasts don't download
#TBR, WSN, BAL, MIL
def iterate_broadcast(teams, downloadedFiles):

	for team in sorted(teams.keys()):
		results = download_broadcast(teams[team], team)

		if results['html'] is True:
			continue
		
		print('Downloading broadcast     for {0}: \t link: {1}'.format(team, teams[team]['broadcast']))
		
		data = results['datafile']
		downloadedFiles[team]['Broadcast'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

	return True	

def iterate_promo(teams, downloadedFiles):

	teams = get_promos(teams)
	for team in sorted(teams.keys()):
		results = download_promo(teams[team], team)
		
		if results['html'] is True:
			continue
		
		print('Downloading promo     for {0}: \t link: {1}'.format(team, teams[team]['promo']))
		
		data = results['datafile']
		downloadedFiles[team]['Promo'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

	return True

def iterate_allergy(teams, downloadedFiles):
	allergycodes = get_allergycodes()
	urls = []
	for team in sorted(teams.keys()):
		results = download_allergy(teams[team], team, iterate_allergy)
		
		if results['html'] is True:
			continue

		print('Downloading pollen     for {0}: \t link: {1}'.format(team, teams[team]['allergy']))
		
		data = results['datafile']
		url = results['url']
		[urls.append(link) for link in url if link not in urls]
		downloadedFiles[team]['Allergy'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data), 'URL': url}

	return urls

def load_teams():
	teams = defaultdict(dict)
	downloadedFiles = defaultdict(dict)
	teamdata = csv.DictReader(open("Data/MLB 2013 Req Daily Info - Websites.csv"))
	
	for rows in teamdata:
		teams[rows['TEAM']] = {key.lower(): value.strip() for key, value in rows.items() if not key == 'TEAM'} 
	
	for team in teams.keys():
		downloadedFiles[team] = defaultdict(dict)
	
	overall = teams.pop('ALL')

	return teams, overall, downloadedFiles

def make_email(teams, overall, downloadedFiles):
	pass

def main():
	teams, overall, downloadedFiles = load_teams()
	iterate_stats(teams, downloadedFiles)
	iterate_schedules(teams, downloadedFiles)
	iterate_promo(teams, downloadedFiles)
	iterate_broadcast(teams, downloadedFiles)
	iterate_allergy(teams, downloadedFiles)
	return teams

if __name__ == "__main__":
	main()



