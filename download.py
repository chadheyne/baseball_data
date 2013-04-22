#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib
import urllib.request
import datetime
import time
import csv
import os


def download_stats(team, name):
	if not team['stats'].endswith('shtml'):
		return
	date = time.strftime("_%m_%d_%Y")	
	print(team['stats'])
	datafile = os.path.join('Data', 'Stats', name+date+".csv")
	csvf = open(datafile, "a", encoding='utf-8', newline = '')
	stats = BeautifulSoup(urllib.request.urlopen(team['stats']))
	for table in stats.find_all('table'):
		for row in table.find_all('tr'):
			col = row.get_text().split('\n')
			csvf.write('| '.join(col))
			csvf.write('\n')
	csvf.close()

def download_schedules(team, name):
	if not team['schedules'].endswith('shtml'):
		return
	date = time.strftime("_%m_%d_%Y")	
	print(team['schedules'])
	datafile = os.path.join('Data', 'Schedules', name+date+".csv")
	csvf = open(datafile, "a", encoding='utf-8', newline = '')
	schedules = BeautifulSoup(urllib.request.urlopen(team['schedules']))
	for table in schedules.find_all('table'):
		for row in table.find_all('tr'):
			col = row.get_text().split('\n')
			csvf.write('| '.join(col))
			csvf.write('\n')
	csvf.close()



def download_broadcast(team, name):
	print(name)
	if not team['broadcast'].endswith(name.lower()):
		return
	date = time.strftime("_%m_%d_%Y")	
	print(team['broadcast'])
	datafile = os.path.join('Data', 'Broadcast', name+date+".csv")
	csvf = open(datafile, "a", encoding='utf-8', newline = '')
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
	datafile = os.path.join('Data', 'Allergy', name+date+".csv")
	csvf = open(datafile, "a", encoding='utf-8', newline = '')
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


if __name__ == "__main__":
	teams = {}
	reader = csv.reader(open("Data/MLB 2013 Req Daily Info - Websites.csv"))
	for rows in reader:
		team = {}
		name = rows[0]
		team['broadcast'], team['promo'], team['stats'], team['schedules'], team['allergy'], team['standings'], team['wildcardStandings'] = rows[1:]
		teams[name] = team
	for team, pages in teams.items():
		#download_stats(teams[team], team)
		#print('Sleeping....')
		#time.sleep(42)
		#download_schedules(teams[team], team)
		#print('Sleeping....')
		#time.sleep(42)
		download_broadcast(teams[team], team)
		
		