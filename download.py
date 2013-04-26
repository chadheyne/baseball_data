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

	directory = os.path.join('Data', date, 'Stats')
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

	directory = os.path.join('Data', date, 'Schedules')
	
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
	
	directory = os.path.join('Data', date, 'Broadcast')
	
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
	
	directory = os.path.join('Data', date, 'Allergy')
	
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

	if codes:
		nums = [codes[i] for i in urls]
		results = list(zip(days, imgs, urls, nums))
		csvf.writerow(['City/Zip', 'Date', 'URL', 'Value'])
	else:
		results = list(zip(days, imgs, urls))
		csvf.writerow(['City/Zip', 'Date', 'URL', 'Value'])
	csvf.writerow([city, date[1:]])
	csvf.writerows(results)
	return {'html': allergy, 'datafile': datafile, 'url': urls}

def download_promo(team, name):
	
	if not team['promo']:
		return
	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', date, 'Promo')
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

def download_standings(team, name='Full_Standings'):
	if not team['standings']:
		return 

	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', date, 'Standings')
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['standings']))
		return {'html': True, 'datafile': datafile}

	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	standings = BeautifulSoup(urllib.request.urlopen(team['standings']))

	for table in standings.find_all('table'):
		
		for row in table.find_all('tr'):
			cols = [col.text for col in row.find_all('td')]			
			csvf.writerow(cols)
			
	infile.close()

	return {'html': standings, 'datafile': datafile}

def download_wildcard(team, name='Wildcard'):
	if not team['wildcard standings']:
		return 

	date = time.strftime("_%m_%d_%Y")	
	
	directory = os.path.join('Data', date, 'Standings')
	if not os.path.exists(directory):
		os.makedirs(directory)

	datafile = os.path.join(directory,name+date+".csv")

	if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
		print("Already got this one: Team - {0} \t URL - {1}".format(name, team['wildcard standings']))
		return {'html': True, 'datafile': datafile}

	infile = open(datafile, "w", encoding='utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	wildcard = BeautifulSoup(urllib.request.urlopen(team['wildcard standings']))

	for table in wildcard.find_all('table'):
		
		for row in table.find_all('tr'):
			cols = [col.text for col in row.find_all('td')]			
			csvf.writerow(cols)
			
	infile.close()

	return {'html': wildcard, 'datafile': datafile}	

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

def get_allergycodes(date):

	allergy = defaultdict(dict)

	allergydata = csv.DictReader(open("Data/"+date+"allergycodes"+date+".csv"))
	for row in allergydata:
		allergy[row['URL']] = row['value']

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

def iterate_broadcast(teams, downloadedFiles):

	for team in sorted(teams.keys()):
		results = download_broadcast(teams[team], team)

		if results['html'] is True:
			continue
		
		print('Downloading broadcast     for {0}: \t link: {1}'.format(team, teams[team]['broadcast']))
		
		data = results['datafile']
		downloadedFiles[team]['Broadcast'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

	return True	

def iterate_promo(teams, downloadedFiles, mainQt=False):

	if mainQt is False:
		teams = get_promos(teams)
	
	for team in sorted(teams.keys()):
		print(teams[team].keys())
		#try:
		#	if not teams[team]['html']:
		#		print("No HTML here.")
		#		continue
		#except KeyError:
		#	print(teams[team].keys())
		#	continue
		results = download_promo(teams[team], team)
		
		if results['html'] is True:
			continue
		
		print('Downloading promo     for {0}: \t link: {1}'.format(team, teams[team]['promo']))
		
		data = results['datafile']
		downloadedFiles[team]['Promo'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

	return True

def iterate_allergy(teams, downloadedFiles, havenewCodes = False):
	allergycodes = False
	if havenewCodes:
		allergycodes = get_allergycodes()

	urls = []
	for team in sorted(teams.keys()):
		results = download_allergy(teams[team], team, allergycodes)
		
		if results['html'] is True:
			continue

		print('Downloading pollen     for {0}: \t link: {1}'.format(team, teams[team]['allergy']))
		
		data = results['datafile']
		url = results['url']
		[urls.append(link) for link in url if link not in urls]
		downloadedFiles[team]['Allergy'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data), 'URL': url}

	return urls

def iterate_overall(overall, downloadedFiles):

	wildcard = download_wildcard(overall)
	if wildcard['html'] is not True:
		print('Downloading wildcard     for {0}: \t link: {1}'.format(overall, overall['wildcard standings']))
	
	data_wild = wildcard['datafile']
	downloadedFiles['ALL']['Wildcard'] = {'File': os.path.abspath(data_wild), 'Size': os.path.getsize(data_wild)}	

	standings = download_standings(overall)
	if standings['html'] is not True:
		print('Downloading standings     for {0}: \t link: {1}'.format(overall, overall['standings']))
	
	data_stand = standings['datafile']
	downloadedFiles['ALL']['Standings'] = {'File': os.path.abspath(data_stand), 'Size': os.path.getsize(data_stand)}

	return True

def load_teams():
	teams = defaultdict(dict)
	downloadedFiles = defaultdict(dict)
	teamdata = csv.DictReader(open("Data/MLB 2013 Req Daily Info - Websites.csv"))
	
	for rows in teamdata:
		teams[rows['TEAM']] = {key.lower(): value.strip() for key, value in rows.items() if not key == 'TEAM'} 
	
	for team in teams.keys():
		downloadedFiles[team] = defaultdict(dict)
	
	overall = teams.pop('ALL')
	overall = {key: val for key, val in overall.items() if val}

	return teams, overall, downloadedFiles

def make_list(teams, overall, downloadedFiles):
	
	date = time.strftime("_%m_%d_%Y")	
	
	infile = open('Data/'+date+'/List'+date+'.csv', 'w', encoding = 'utf-8', newline = '')
	csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

	new_allergy = open('Data/'+date+'/allergycodes'+date+'.csv', 'w', encoding = 'utf-8', newline = '')
	allergy_csv = csv.writer(new_allergy, quoting=csv.QUOTE_ALL)
	allergy_csv.writerow(['TEAM', 'Allergy', 'id', 'URL', 'value'])

	for team, data in sorted(downloadedFiles.items()):
		for point, contents in data.items():
			
			if point == 'Allergy':
				for key, value in contents.items():
						if key == 'URL':

							first_url = value[0]
							allergy_csv.writerow([team, point, key, first_url, ''])
							[allergy_csv.writerow(['','', key, url, '']) for url in value[1:]]
				
				csvf.writerow([team, point, 'Size', contents['Size'], 'File', contents['File'] ])

			else:
				try:
					csvf.writerow([team, point, 'Size', contents['Size'], 'File', contents['File'] ])
				except KeyError:
					csvf.writerow(['Some error happened here', team, point])
	
	new_allergy.close()
	infile.close()
	return True

def processGUI(command, teams, overall, downloadedFiles, subcommand=False):

	if command == 'iterate_allergy':
		start = time.time()
		iterate_allergy(teams, downloadedFiles, subcommand) #subcommand allows us to dictate whether the file is updated
		minutes, seconds = divmod(time.time() - start, 60)
		print('\n\n\nFinished downloading allergy data: {0} minutes and {1} seconds'.format(minutes, seconds))
		make_list(teams, overall, downloadedFiles)
	
	elif command == 'iterate_stats':
		start = time.time()
		iterate_stats(teams, downloadedFiles)
		minutes, seconds = divmod(time.time() - start, 60)
		print('\n\n\nFinished downloading stats data: {0} minutes and {1} seconds'.format(minutes, seconds))
		make_list(teams, overall, downloadedFiles)
	
	elif command == 'iterate_schedules':
		start = time.time()
		iterate_schedules(teams, downloadedFiles)	
		minutes, seconds = divmod(time.time() - start, 60)
		print('\n\n\nFinished downloading schedules data: {0} minutes and {1} seconds'.format(minutes, seconds))
		make_list(teams, overall, downloadedFiles)
	
	elif command == 'iterate_promo':
		start = time.time()
		iterate_promo(teams, downloadedFiles, True)
		minutes, seconds = divmod(time.time() - start, 60)
		print('\n\n\nFinished downloading promo data: {0} minutes and {1} seconds'.format(minutes, seconds))
		make_list(teams, overall, downloadedFiles)
	
	elif command == 'iterate_broadcast':
		start = time.time()
		iterate_broadcast(teams, downloadedFiles)
		minutes, seconds = divmod(time.time() - start, 60)
		print('\n\n\nFinished downloading broadcast data: {0} minutes and {1} seconds'.format(minutes, seconds))
		make_list(teams, overall, downloadedFiles)
	
	elif command == 'iterate_overall':
		start = time.time()
		iterate_overall(overall, downloadedFiles)
		minutes, seconds = divmod(time.time() - start, 60)
		print('\n\n\nFinished downloading allergy data: {0} minutes and {1} seconds'.format(minutes, seconds))
		make_list(teams, overall, downloadedFiles)
	
	elif command == 'iterate_all':
		
		start = time.time()
		iterate_stats(teams, downloadedFiles)
		iterate_schedules(teams, downloadedFiles)
		iterate_promo(teams, downloadedFiles)
		iterate_broadcast(teams, downloadedFiles)
		iterate_allergy(teams, downloadedFiles)
		iterate_overall(overall, downloadedFiles)
		minutes, seconds = divmod(time.time() - start, 60)
		
		make_list(teams, overall, downloadedFiles)
		
		if subcommand is True:
			send_update(True)
		
		elif subcommand is 'email_sum':
			send_update(False)
		
		else:
			print('No emails')

		print('\n\n\nFinished downloading all of the data: {0} minutes and {1} seconds'.format(minutes, seconds))
	
	elif command == 'send_email':
		if subcommand is True:
			send_update(True)
		elif subcommand is 'email_sum':
			send_update(False)
		else:
			print('No emails')	
	


def ocr_images(urls, downloadedFiles):
	from tesserwrap import Tesseract
	from PIL import Image
	import io

	for url in urls:

		pic = io.BytesIO(urllib.request.urlopen(url).read())

		img = Image.open(pic)
		tr = Tesseract()
		text = tr.ocr_image(img)
		print(text.split('\n')[0])

		

def send_update(wantZip = True):
	import email_data

	date = time.strftime("_%m_%d_%Y")
	directory = os.path.join('Data/', date)
	date.translate(str.maketrans('_', '/'))
	email_data.send_email(date, directory, wantZip) #Add third argument sendZip = False in order to only send main results

	return True


def main():
	
	start = time.time()
	teams, overall, downloadedFiles = load_teams()
	
	iterate_stats(teams, downloadedFiles)
	
	iterate_schedules(teams, downloadedFiles)
	
	iterate_promo(teams, downloadedFiles)
	
	iterate_broadcast(teams, downloadedFiles)
	
	iterate_allergy(teams, downloadedFiles)
	
	iterate_overall(overall, downloadedFiles)
	
	make_list(teams, overall, downloadedFiles)
	
	minutes, seconds = divmod(time.time() - start, 60)
	print("Finished downloading all of the data: {0} minutes and {1} seconds".format(minutes, seconds))

	return teams

if __name__ == "__main__":
	main()



