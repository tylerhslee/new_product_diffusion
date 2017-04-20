# -*- coding: utf-8 -*-

'''
Retrieve information of interest by parsing the HTML document

Classes:
    URLCollector
    DataCollector
'''

import re
import html

import requests
import numpy as np

from bs4 import BeautifulSoup


class URLCollector():
    '''
    Parses relevent URLs from the table inside the HTML document.
    '''
    def __init__(self, url, index=0, class_=None, type_=None, **kwargs):
        '''
        Takes the URL Of the target webpage as argument.
        index=0 by default because most of the times only the first occurrence
        is needed. The parameter affects which table is retrived from the doc.
        class_ parameter determines which table to target.
            "index_chart" for weekly regions
            "chart" for weekly regional rankings
        '''
        self.doc = requests.get(url).text
        self.soup = BeautifulSoup(self.doc)
        self.table = self._get_table(class_=class_)
        self.entry = self._get_entry(index, type_, **kwargs)

    def _get_table(self, class_=None):
        return self.soup.find_all("table", class_=class_)

    def _get_entry(self, index, type_, **kwargs):
        return self.table[index].find_all(type_, **kwargs)

# ============================================================================

class DataCollector():
    '''
    Stores relevant data in easily accessible formats
    '''
    # Below are regexes to extract the data from each tag.
    # Because they are used in every region for every week,
    # it's better to compile them statically.
    title_pattern = \
        r'"(http://www\.vgchartz\.com/game/(\d+)/.+?/)".+?>(.+?)</a>'
    title_regex = re.compile(title_pattern)

    platform_pattern = \
        r'"(http://www\.vgchartz\.com/platform/(\d+)/.+?/)">(.+?)</a>'
    platform_regex = re.compile(platform_pattern)

    devgen_pattern = \
        r'"(http://www\.vgchartz\.com/companies/(?:(\d+)/.+?/)?)">' \
        r'(?:(.+?))?</a>, (.+?)</td>'
    devgen_regex = re.compile(devgen_pattern)

    # ========================================================================

    def __init__(self, entry):
        '''
        Takes the ResultsSet from the result of the parser and extracts
        relevant information using the regex.
        
        Because the entry is type ResultSet, every lowest-level element needs
        to be converted to type string.
        '''
        self.entry = entry

    def extract_weekly_region(self):
        '''
        Returns a json of regional data useful to structuring the individual
        game title data extracted through each URL.

        json = {
            week: (int) Week ID
                [{
                       url: (string) Direct link to the game ranking
                    region: (string) Region name as shown in the link
                 }]
        }
        '''
        print("Weekly Regional: Received %d entries" % len(self.entry))
        pattern = \
            r'<a href="(http://www\.vgchartz\.com/weekly/(\d+)/.+?/)">(.+?)<'
        regex = re.compile(pattern)
        json = {}
        
        for tag in self.entry:
            # If no region for that week, continue
            missing_data = '-'
            if tag.get_text() == missing_data:
                continue

            # Convert bs4.element.Tag to string before applying regex
            raw = regex.findall(str(tag))[0]
            week = int(raw[1])
            data_point = {
                    'url': raw[0],
                    'region': raw[2]
                    }
            
            # Handle creation of new keys (new week ID)
            try:
                json[week].append(data_point)
            except KeyError:
                json[week] = []
                json[week].append(data_point)
        return json

    # ========================================================================
    
    def extract_regional_ranking(self):
        '''
        Returns a JSON of weekly ranking data.

        json = {
            region (string): {
                week (int):
                    [{
                              pos: (int) Rank of the game
                            title: (string) Title of the game
                         platform: (string) Platform sold to
                        developer: (string) Developed by
                            genre: (string) Genre
                           weekly: (string) Weekly unit sales
                            total: (string) Total unit sales
                         week_num: (int) Number of weeks since release
                    }]
            }
        }
        "Pro" sales means "N/A"
        '''
        print("Regional Ranking: Received %d entries" % len(self.entry))

        # Alias to the Class because the name is too long...
        C = DataCollector

        # Ignore the first row because it's the header row
        ranking = self.entry[1:]

        # Return a list of data on the games in the ranking
        ret = []
        
        # Because of the non-recursive option, the HTML doc is parsed a 
        # little weirdly. Below are the indices for the important tags 
        # in each entry.
        pos_index = 1
        meat_index = 3      # title, platform, developer, genre
        weekly_sales_index = 5
        total_sales_index = 7
        week_num_index = 9

        for game in ranking:
            game = list(game)
            pos = game[pos_index].get_text()
            weekly = game[weekly_sales_index].get_text()
            total = game[total_sales_index].get_text()
            week_num = game[week_num_index].get_text()
            
            meat = str(game[meat_index])
            # Group 0: URL
            # Group 1: ID
            # Group 2: Name
            title = C.title_regex.findall(meat)[0]
            platform = C.platform_regex.findall(meat)[0]
            devgen = C.devgen_regex.findall(meat)[0]

            # Deal with empty strings when converting IDs to int
            # ID = 0 if there is no ID
            def convert_id_to_int(s):
                s = s.strip()
                return int(s) if s else 0

            data_point = {
                    # title ===========================
                    'title_name':     html.unescape(str(title[2])),
                    'title_id':       int(title[1]),
                    'title_url':      html.unescape(str(title[0])),
                    # platform ========================
                    'platform_name':  html.unescape(str(platform[2])),
                    'platform_id':    int(platform[1]),
                    'platform_url':   html.unescape(str(platform[0])),
                    # developer =======================
                    'developer_name': html.unescape(str(devgen[2])),
                    'developer_id':   str(devgen[1]),
                    'developer_url':  html.unescape(str(devgen[0])),
                    # misc ============================
                    'rank':           int(pos),
                    'genre':          html.unescape(str(devgen[3])),
                    'weekly_sales':   html.unescape(str(weekly)),
                    'total_sales':    html.unescape(str(total)),
                    'week_num':       int(week_num)
                    }
            ret.append(data_point)
        return ret
