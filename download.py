#!/usr/bin/env python

from bs4 import BeautifulSoup
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from collections import defaultdict, deque
from selenium import webdriver

import urllib
import urllib.request
import sys
import time
import csv
import os
import datetime


def download_stats(team, name):

    if not team['stats'].endswith('shtml'):
        return

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Stats')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['stats']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    stats = BeautifulSoup(urllib.request.urlopen(team['stats']), 'html.parser')

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
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Schedules')

    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['schedules']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    schedules = BeautifulSoup(urllib.request.urlopen(team['schedules']), 'html.parser')

    for table in schedules.find_all('table'):

        if 'cellspacing' in table.attrs:
            if not table.find('td').get_text() == 'Season Summary':

                header = [head.get_text() for head in table.find_all('th')]
                headers = []
                [headers.append(item) for item in header if item not in headers]
                data = [entry.text.strip() for entry in table.find_all('td') if not entry.find_all('th') and 'colspan' not in entry.attrs]
                tablenames = [entry.text.strip() for entry in table.find_all('td') if not entry.find_all('th') and 'colspan' in entry.attrs]
                data = {data[i]: data[i:i+6] for i in range(0, len(data), 6)}  # Create a dict for the 'table name'

                for line in table.text.split('\n'):  # "Clever" hack to write tables as they appear in the data
                    if line == 'SplitWLRSRAWP':
                        csvf.writerow(headers)
                    elif line in tablenames:
                        csvf.writerow(['', '', line])
                    else:
                        test = [item for item in line.split(' ') if item]
                        empty = []
                        for item in test:
                            try:
                                int(item)
                            except ValueError:
                                try:
                                    float(item)
                                except ValueError:
                                    empty.append(item)
                        rowName = ' '.join(empty)
                        if rowName in data.keys():
                            csvf.writerow(data[' '.join(empty)])

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
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Broadcast')

    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['broadcast']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    broadcast = BeautifulSoup(urllib.request.urlopen(team['broadcast']), 'html.parser')

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
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Allergy')

    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0 and not codes:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['allergy']))
        return {'html': True, 'datafile': datafile, 'url': 'Already downloaded'}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    allergy = BeautifulSoup(urllib.request.urlopen(team['allergy']), 'html.parser')

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


def download_promo(team, name, driver):

    if not team['promo']:
        return
    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Promo')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['promo']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    driver.get(team['promo'])

    promo = BeautifulSoup(driver.page_source, 'html.parser')
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
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Standings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['standings']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    standings = BeautifulSoup(urllib.request.urlopen(team['standings']), 'html.parser')

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
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Standings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['wildcard standings']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    wildcard = BeautifulSoup(urllib.request.urlopen(team['wildcard standings']), 'html.parser')

    for table in wildcard.find_all('table'):

        for row in table.find_all('tr'):
            cols = [col.text for col in row.find_all('td')]
            csvf.writerow(cols)

    infile.close()

    return {'html': wildcard, 'datafile': datafile}


def download_altwildcard(team, driver, name='Alt Wildcard'):
    if not team['wildcard']:
        return

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Standings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['wildcard']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    #driver = webdriver.PhantomJS('phantomjs')
    driver.get(team['wildcard'])
    wildcard = BeautifulSoup(driver.page_source, 'html.parser')

    for table in wildcard.find_all('table'):
        if 'data_grid' not in table.attrs['class']:
            continue

        for row in table.find_all('tr'):
            if row.find_all('th'):
                head = [h.text for h in row.find_all('th')]
                csvf.writerow(head)
            cols = [col.text for col in row.find_all('td')]
            csvf.writerow(cols)

    infile.close()

    return {'html': wildcard, 'datafile': datafile}


def download_teambatting(team, name='Batting'):
    if not team['batting']:
        return

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Standings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['batting']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    batting = BeautifulSoup(urllib.request.urlopen(team['batting']), 'html.parser')

    for table in batting.find_all('table'):

        for row in table.find_all('tr'):
            cols = [col.text for col in row.find_all('td')]
            csvf.writerow(cols)

    infile.close()

    return {'html': batting, 'datafile': datafile}


def download_teampitching(team, name='Pitching'):
    if not team['pitching']:
        return

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR, 'Standings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    datafile = os.path.join(directory, name+date+".csv")

    if os.path.exists(datafile) and os.path.getsize(datafile) > 0:
        print("Already got this one: Team - {0} \t URL - {1}".format(name, team['pitching']))
        return {'html': True, 'datafile': datafile}

    infile = open(datafile, "w", encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    pitching = BeautifulSoup(urllib.request.urlopen(team['pitching']), 'html.parser')

    for table in pitching.find_all('table'):

        for row in table.find_all('tr'):
            cols = [col.text for col in row.find_all('td')]
            csvf.writerow(cols)

    infile.close()

    return {'html': pitching, 'datafile': datafile}


def get_allergycodes(date):

    allergy = defaultdict(dict)
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    allergydata = csv.DictReader(open(DATA_DIR+"/allergycodes"+date+".csv"))
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


def iterate_promo(teams, downloadedFiles, driver):

    for team in sorted(teams.keys()):
        print(teams[team].keys())

        results = download_promo(teams[team], team, driver)

        if results['html'] is True:
            continue

        print('Downloading promo     for {0}: \t link: {1}'.format(team, teams[team]['promo']))

        data = results['datafile']
        downloadedFiles[team]['Promo'] = {'File': os.path.abspath(data), 'Size': os.path.getsize(data)}

    return True


def iterate_allergy(teams, downloadedFiles, havenewCodes=False):
    allergycodes = False
    if havenewCodes:
        date = time.strftime("_%m_%d_%Y")
        allergycodes = get_allergycodes(date)

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


def iterate_overall(overall, downloadedFiles, driver):

    wildcard = download_wildcard(overall)
    if wildcard['html'] is not True:
        print('Downloading wildcard     for {0}: \t link: {1}'.format(overall, overall['wildcard standings']))

    data_wild = wildcard['datafile']
    downloadedFiles['ALL']['Wildcard'] = {'File': os.path.abspath(data_wild), 'Size': os.path.getsize(data_wild)}

    alt_wildcard = download_altwildcard(overall, driver)
    if alt_wildcard['html'] is not True:
        print('Downloading wildcard     for {0}: \t link: {1}'.format(overall, overall['wildcard']))

    data_alt_wild = alt_wildcard['datafile']
    downloadedFiles['ALL']['Alt Wildcard'] = {'File': os.path.abspath(data_alt_wild), 'Size': os.path.getsize(data_alt_wild)}

    standings = download_standings(overall)
    if standings['html'] is not True:
        print('Downloading standings     for {0}: \t link: {1}'.format(overall, overall['standings']))

    data_stand = standings['datafile']
    downloadedFiles['ALL']['Standings'] = {'File': os.path.abspath(data_stand), 'Size': os.path.getsize(data_stand)}

    batting = download_teambatting(overall)
    if batting['html'] is not True:
        print('Downloading batting     for {0}: \t link: {1}'.format(overall, overall['batting']))

    data_batting = standings['datafile']
    downloadedFiles['ALL']['Batting'] = {'File': os.path.abspath(data_batting), 'Size': os.path.getsize(data_batting)}

    pitching = download_teampitching(overall)
    if pitching['html'] is not True:
        print('Downloading pitching     for {0}: \t link: {1}'.format(overall, overall['pitching']))

    data_pitching = standings['datafile']
    downloadedFiles['ALL']['Pitching'] = {'File': os.path.abspath(data_pitching), 'Size': os.path.getsize(data_pitching)}

    return True


def load_teams():
    teams = defaultdict(dict)
    downloadedFiles = defaultdict(dict)
    team_file = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', 'MLB 2013 Req Daily Info - Websites.csv'))
    teamdata = csv.DictReader(open(team_file))

    for rows in teamdata:
        teams[rows['TEAM']] = {key.lower(): value.strip() for key, value in rows.items() if not key == 'TEAM'}

    for team in teams.keys():
        downloadedFiles[team] = defaultdict(dict)

    overall = teams.pop('ALL')
    overall = {key: val for key, val in overall.items() if val}

    return teams, overall, downloadedFiles


def make_list():

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    infile = open(DATA_DIR+'/List'+date+'.csv', 'w', encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)

    csvf.writerow(['Team', 'Content', 'Size', 'Size', 'File', 'Full Path'])
    for root, dirs, files in os.walk(DATA_DIR):
        for f in files:
            if not f.endswith('.csv') or f.startswith('List') or f.startswith('allergycodes'):
                continue
            point = os.path.dirname(os.path.join(root, f)).split('/')[-1]
            team = f.split('_')[0]
            fullname = os.path.abspath(os.path.join(root, f))
            size = os.path.getsize(fullname)
            csvf.writerow([team, point, '', size, '', fullname])

    infile.close()
    return True


def new_allergies(links):

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))

    infile = open(DATA_DIR+'/allergycodes'+date+'.csv', 'a', encoding='utf-8', newline='')
    csvf = csv.writer(infile, quoting=csv.QUOTE_ALL)
    csvf.writerow(['URL', 'value'])
    for link in links:
        csvf.writerow(['http://' + link, None])
        directory = os.path.join(DATA_DIR, 'Images')
        if not os.path.exists(directory):
            os.makedirs(directory)
        imgname = '_'.join(link.split('%')[1:]) + '.gif'
        local_file = open(os.path.join(directory, imgname), 'wb')
        local_file.write(urllib.request.urlopen('http://'+link).read())
        local_file.close()


def processGUI(command, teams, overall, downloadedFiles, subcommand=False):
    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    f = open(DATA_DIR+'/Log.txt', 'a')

    driver = webdriver.PhantomJS('phantomjs')

    sys.stdout = f
    if command == 'iterate_allergy':
        start = time.time()
        print('\n\n\nStarted downloading allergy data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        newcodes = iterate_allergy(teams, downloadedFiles, subcommand)  # subcommand allows us to dictate whether the file is updated
        minutes, seconds = divmod(time.time() - start, 60)
        print('\n\n\nFinished downloading allergy data: {0} minutes and {1} seconds'.format(minutes, seconds))
        make_list()
        new_allergies(newcodes)
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()

    elif command == 'iterate_stats':
        start = time.time()
        print('\n\n\nStarted downloading stats data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        iterate_stats(teams, downloadedFiles)
        minutes, seconds = divmod(time.time() - start, 60)
        print('\n\n\nFinished downloading stats data: {0} minutes and {1} seconds'.format(minutes, seconds))
        make_list()
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()

    elif command == 'iterate_schedules':
        start = time.time()
        print('\n\n\nStarted downloading schedules data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        iterate_schedules(teams, downloadedFiles)
        minutes, seconds = divmod(time.time() - start, 60)
        print('\n\n\nFinished downloading schedules data: {0} minutes and {1} seconds'.format(minutes, seconds))
        make_list()
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()

    elif command == 'iterate_promo':
        start = time.time()
        print('\n\n\nStarted downloading promo data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        iterate_promo(teams, downloadedFiles, driver)
        minutes, seconds = divmod(time.time() - start, 60)
        print('\n\n\nFinished downloading promo data: {0} minutes and {1} seconds'.format(minutes, seconds))
        make_list()
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()

    elif command == 'iterate_broadcast':
        start = time.time()
        print('\n\n\nStarted downloading broadcast data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        iterate_broadcast(teams, downloadedFiles)
        minutes, seconds = divmod(time.time() - start, 60)
        print('\n\n\nFinished downloading broadcast data: {0} minutes and {1} seconds'.format(minutes, seconds))
        make_list()
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()

    elif command == 'iterate_overall':
        start = time.time()
        print('\n\n\nStarted downloading overall data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        iterate_overall(overall, downloadedFiles, driver)
        minutes, seconds = divmod(time.time() - start, 60)
        print('\n\n\nFinished downloading overall data: {0} minutes and {1} seconds'.format(minutes, seconds))
        make_list()
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()

    elif command == 'iterate_all':

        start = time.time()
        print('\n\n\nStarted downloading all of the data: {0}'.format(datetime.datetime.now().strftime('%A %B, %Y: %H:%M:%S %p')))
        iterate_stats(teams, downloadedFiles)
        iterate_schedules(teams, downloadedFiles)
        iterate_broadcast(teams, downloadedFiles)
        try:
            newcodes = iterate_allergy(teams, downloadedFiles, True)
        except FileNotFoundError:
            newcodes = iterate_allergy(teams, downloadedFiles, False)
            new_allergies(newcodes)

        iterate_promo(teams, downloadedFiles, driver)
        iterate_overall(overall, downloadedFiles, driver)
        minutes, seconds = divmod(time.time() - start, 60)

        make_list()
        print('\n\n\nFinished downloading all of the data: {0} minutes and {1} seconds'.format(minutes, seconds))

        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()
        if subcommand is True:
            send_update(True)

        elif subcommand is 'email_sum':
            send_update(False)

        else:
            print('No emails')

    elif command == 'send_email':
        sys.stdout.flush()
        sys.stdout = sys.__stdout__
        f.close()
        if subcommand is True:
            send_update(True)
        elif subcommand is 'email_sum':
            send_update(False)
        else:
            print('No emails')


def send_update(wantZip=True):
    import email_data

    date = time.strftime("_%m_%d_%Y")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'Data', date))
    directory = os.path.join(DATA_DIR)
    date.translate(str.maketrans('_', '/'))
    email_data.send_email(date, directory, wantZip)  # Add third argument sendZip = False in order to only send main results

    return True


def main():
    teams, overall, downloadedFiles = load_teams()
    iterate_promo(teams, downloadedFiles, False)
    processGUI(iterate_all, teams, overall, downloadedFiles, True)

if __name__ == "__main__":
    main()
