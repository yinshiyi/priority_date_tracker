import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import os
import seaborn as sns
from datetime import datetime, date, time, timezone
import matplotlib.pyplot as plt


base_url = 'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{}/visa-bulletin-for-{}-{}.html'
# 2005 is the first year of china backlog at all
# 2007 is the first year of china backlog monthly
# 2015oct is the first year of 4 tables
# https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2016/visa-bulletin-for-october-2015.html
# this is a big jump month and the divergence of the finalaction and priority
# https://www.myprioritydate.com/VisaBulletin
# 2007
years = range(2022, 2024)[::-1]
months = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december'][::-1]
master_list=[]
master_list_long=[]
df_list_long = [pd.DataFrame() for _ in range(4)]
for year in years:
    for month in months:
        # the website treats the last quarter differently
        if month in ['october', 'november', 'december']:
            url = base_url.format(str(year+1), month, str(year))
        else:
            url = base_url.format(str(year), month, str(year))
        print(url)
        timeout = random.randint(3, 30)
        print(f"Accessing URL: {url} (timeout: {timeout} seconds)")
        time.sleep(timeout)
        # web scraping code here
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        china_tables = []
        tables = soup.find_all('table')
        # loop through each table on the page
        for table in tables:
            # find all the rows in the table
            table_rows = table.find_all('tr')
            # loop through each row
            for row in table_rows:
                # find all the cells in the row
                cells = row.find_all('td')
                # loop through each cell
                for cell in cells:
                    # check if the cell contains the string "CHINA"
                    if "CHINA" in cell.get_text():
                        # add the table to the list of tables if it hasn't been added already
                        if table not in china_tables:
                            china_tables.append(table)

        df_list = []
        for i, table in enumerate(china_tables):
            rows = table.find_all('tr')
            columns = [cell.get_text().strip() for cell in rows[0].find_all('td')]
            data = []
            for row in rows[1:]:
                data.append([cell.get_text().strip() for cell in row.find_all('td')])
            df = pd.DataFrame(data, columns=columns)
            df.replace('U', pd.NA, inplace=True)
            # unpivot the scores columns into rows
            df_long = pd.melt(df, id_vars=df.columns[0], value_vars=df.columns[1:],
                var_name='countries', value_name='date_gov')
            df_long['date'] = pd.to_datetime('01' + month + str(year))
            df_long.loc[df_long['date_gov'] == 'C', 'date_gov'] = (df_long.loc[df_long['date_gov'] == 'C', 'date'])
            df_long['date_gov'] = pd.to_datetime(df_long['date_gov'])
            df_long['delay']=df_long['date']-df_long['date_gov']
            df_long['delay_days'] = df_long['delay'].dt.days
            df_long.columns.values[0] = 'VisaType'
            if not df.empty:
                df_list.append(df)
                if len(china_tables)==4:
                    df_list_long[i] = pd.concat([df_list_long[i],df_long], axis=0)
                else:
                    # when only two table is avaiable, only update #1 to #1_df, #2 to #3_df
                    df_list_long[2*(i > 0)] = pd.concat([df_list_long[2*(i > 0)],df_long], axis=0)
                    df_list_long[2*(i > 0)+1] = pd.concat([df_list_long[2*(i > 0)+1],df_long], axis=0)


        for i, table in enumerate(df_list):
            print(f"Table {i+1}:")
            print(table)
            print("\n")

            ## print all tables indiviually
            # filename = f"data/{year}_{month}_Table_{i+1}.csv"
            # if not os.path.exists('data'):
            #     os.mkdir('data')
            # table.to_csv(filename, index=False)
        if df_list:
            master_list.append({'year': str(year), 'month': month, 'df_list': df_list})
            #master_list_long.append(df_list_long)

# only the last two tables out of the 4 are usefully for employment analysis
finaldate=df_list_long[2]
prioitydate=df_list_long[3]

# seperating the 4 tables
eb2_final=finaldate.loc[(finaldate['VisaType'] == '2nd') & (finaldate['countries'].str.contains('CHINA'))].reset_index(drop=True)
eb2_priority=prioitydate.loc[(prioitydate['VisaType'] == '2nd') & (prioitydate['countries'].str.contains('CHINA'))].reset_index(drop=True)

eb1_final=finaldate.loc[(finaldate['VisaType'] == '1st') & (finaldate['countries'].str.contains('CHINA'))].reset_index(drop=True)
eb1_priority=prioitydate.loc[(prioitydate['VisaType'] == '1st') & (prioitydate['countries'].str.contains('CHINA'))].reset_index(drop=True)

# make individual plots
for table in [eb1_final,eb1_priority]:
    ax = sns.lineplot(data=table, x='date', y='delay_days')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
for table in [eb2_final,eb2_priority]:
    ax = sns.lineplot(data=table, x='date', y='delay_days')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

# concatenate the four tables
merged_table = pd.concat([eb2_final.assign(category='EB2 Final Action Date'),
                          eb2_priority.assign(category='EB2 Priority Date'),
                          eb1_final.assign(category='EB1 Final Action Date'),
                          eb1_priority.assign(category='EB1 Priority Date')])

# create the 4 line plots with legends
ax = sns.lineplot(data=merged_table, x='date', y='delay_days', hue='category')
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

#########################
# print the final tables with timestamp to plot in R later
today = datetime.now()
filename = f"data/{today}_rawdata.csv"
if not os.path.exists('data'):
    os.mkdir('data')
merged_table.to_csv(filename, index=False)

