# -*- coding: utf-8 -*-

import os

import pandas as pd

from Collector import URLCollector, DataCollector


def get_all_URL():
    # We can access all entries through URLCollector.entry attribute.
    weekly_url = "http://www.vgchartz.com/weekly/"
    url_collector = URLCollector(weekly_url,
                                 class_="index_chart",
                                 type_="td",
                                 style="text-align:center;")

    # We can get all data through DataCollector.extract_weekly_region method
    data_collector = DataCollector(url_collector.entry)

    # JSON formatted data that contains region and 
    # corresponding URL organized by each week ID
    return data_collector.extract_weekly_region()

# ============================================================================

def get_ranks(json):
    '''
    Parameter:
        Receive a JSON of all URLs
    Returns: a JSON of retrieved data that can be converted into a DataFrame
    '''
    # Uncomment below to test on sample
    # json = {k: json[k] for k in (42785, 42778, 42771)}

    ret = {}
    for week, result in json.items():
        for entry in result:
            url = entry['url']
            print("Connecting to %s..." % url)

            url_collector = URLCollector(url,
                                         class_="chart",
                                         type_="tr",
                                         recursive=False)
            data_collector = DataCollector(url_collector.entry)
            data_point = data_collector.extract_regional_ranking()

            region = entry['region']
            try:
                catalogue = ret[region]
            except KeyError:
                ret[region] = {}
                catalogue = ret[region]
            finally:
                if week in catalogue.keys():
                    catalogue[week].append(data_point)
                else: catalogue[week] = data_point
    return ret

# ============================================================================

def generate_df(regional_data):
    '''
    Parameter:
        Receive a JSON of regional data, which contains all weeks
    Generate a .csv file that contains all game data

    Each file will be separated by the region because that's the easiest.

    Columns:
    Week Rank Title Platform Developer Genre Weekly_Sales Total_Sales Week_num
    '''
    data = []
    cols = [
            'week', 'rank', 
            'title_name', 'platform_name', 'developer_name',
            'title_id', 'platform_id', 'developer_id',
            'title_url', 'platform_url', 'developer_url',
            'genre', 'weekly_sales', 'total_sales', 'week_num'
            ]
    for week, ranking in regional_data.items():
        week_col = [week] * len(ranking)
        df = pd.DataFrame(ranking)
        df['week'] = week_col
        df = df[cols]
        df.index += 1
        data.append(df)
    return pd.concat(data)

# ============================================================================

def export_csv(region, df):
    target_dir = 'data'
    file_name = region + '.csv'

    # ../data/region.csv
    file_path = os.path.join('..', target_dir, file_name)
    df.to_csv(file_path, index=False)

    print("Exported %s!" % file_name)

# ============================================================================

def main():
    weekly_regional = get_all_URL()
    regional_rankings = get_ranks(weekly_regional)

    regions = [reg for reg in regional_rankings.keys()]
    for region in regions:
        regional_data = regional_rankings[region]
        data_table = generate_df(regional_data)
        export_csv(region, data_table)

    return 0


if __name__ == '__main__':
    exit = main()
    if exit != 0:
        print(exit)
