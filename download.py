#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib
import urllib.request
import datetime
import time
import csv

def download(team, name):
	#if not team['stats'].endswith('shtml'):
	#	return
	date = time.strftime("_%m_%d_%Y")	
	print(team['stats'])
	csvf = open(name + date + ".csv", "a", encoding='utf-8', newline = '')
	stats = BeautifulSoup(urllib.request.urlopen(team['stats']))
	for table in stats.find_all('table'):
		for row in table.find_all('tr'):
			col = row.get_text().split('\n')
			csvf.write('| '.join(col))
			csvf.write('\n')
	csvf.close()


if __name__ == "__main__":
	teams = {}
	reader = csv.reader(open("MLB 2013 Req Daily Info - Websites.csv"))
	for rows in reader:
		team = {}
		name = rows[0]
		team['broadcast'], team['promo'], team['stats'], team['schedules'], team['allergy'], team['standings'], team['wildcardStandings'] = rows[1:]
		teams[name] = team
	for team, pages in teams.items():
		if not teams[team]['stats'].endswith('shtml'):
			continue
		download(teams[team], team)
		print('Sleeping....')
		time.sleep(42)