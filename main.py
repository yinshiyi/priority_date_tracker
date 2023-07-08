import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random
import time
import os
import seaborn as sns
from datetime import datetime, date, time, timezone
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



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

# concatenate the 2 tables
world_merged_table = pd.concat([finaldate.assign(datetype='Final Action Date'),
                          prioitydate.assign(datetype='Priority Date')])
world_merged_table['countries2'] = np.where(world_merged_table['countries'].str.contains('All Chargeability'), 'ROW', 
                          np.where(world_merged_table['countries'].str.contains('CHINA'), 'CHINA', world_merged_table['countries']))

# seperating the 4 tables
eb2_final=finaldate.loc[(finaldate['VisaType'] == '2nd') & (finaldate['countries'].str.contains('CHINA'))].reset_index(drop=True)
eb2_priority=prioitydate.loc[(prioitydate['VisaType'] == '2nd') & (prioitydate['countries'].str.contains('CHINA'))].reset_index(drop=True)

eb1_final=finaldate.loc[(finaldate['VisaType'] == '1st') & (finaldate['countries'].str.contains('CHINA'))].reset_index(drop=True)
eb1_priority=prioitydate.loc[(prioitydate['VisaType'] == '1st') & (prioitydate['countries'].str.contains('CHINA'))].reset_index(drop=True)

# keep the country info, replace long strings into short strings
finaldate['countries2'] = np.where(finaldate['countries'].str.contains('All Chargeability'), 'ROW', 
                          np.where(finaldate['countries'].str.contains('CHINA'), 'CHINA', finaldate['countries']))
prioitydate['countries2'] = np.where(prioitydate['countries'].str.contains('All Chargeability'), 'ROW', 
                          np.where(prioitydate['countries'].str.contains('CHINA'), 'CHINA', prioitydate['countries']))

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

# create the country line plots with legends 
ax.sns.lineplot(data=finaldate.loc[finaldate['VisaType'] == '1st'], x='date', y='delay_days', hue='countries2',style='countries2', alpha=0.5,linewidth=5)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

#########################
# print the final tables with timestamp to plot in R later
today = datetime.now()
filename = f"data/{today}_rawdata.csv"
if not os.path.exists('data'):
    os.mkdir('data')
merged_table.to_csv(filename, index=False)

today = datetime.now()
filename = f"data/{today}_rawdata_world.csv"
if not os.path.exists('data'):
    os.mkdir('data')
world_merged_table.to_csv(filename, index=False)

########################
# facet plot
world_filtered = world_merged_table[(world_merged_table['VisaType'] == '1st') | (world_merged_table['VisaType'] == '2nd')]
world_filtered = world_filtered[~world_filtered['countries2'].str.contains('HONDURAS')]
world_filtered = world_filtered.sort_values('date')
world_filtered['date2'] = world_filtered['date'].dt.strftime('%y-%m')

sns.set(style="ticks")
g = sns.catplot(x="date2", y="delay_days", hue="datetype", col="countries2", row="VisaType",
            data=world_filtered, kind="point", height=2, aspect=3, facet_kws={'sharey': False})
# Set the major tick frequency to every 3 months
g.axes[0,0].xaxis.set_major_locator(ticker.MultipleLocator(3))
# rotation ?????
g.set_xticklabels(rotation=90)


##################
sns.set_style("whitegrid")
g = sns.FacetGrid(world_filtered, row='VisaType', col='countries2', margin_titles=True, ylim=(-10, 4000), sharex=True, sharey=True)
g.map(sns.scatterplot, 'date', 'delay_days', 'datetype', alpha=1, linewidth=0.5, s=5)
g.set_xticklabels(rotation=90)
plt.show()

##############

sns.set(style="ticks")
g = sns.FacetGrid(world_filtered, row='VisaType', col='countries2', margin_titles=True, ylim=(-10, 4000), sharex=True, sharey=True)
g.map(sns.scatterplot, 'date', 'delay_days', 'datetype', alpha=1, linewidth=0.5, s=10)
g.set_xticklabels(rotation=90)
g.set(xticks=world_filtered['date'].unique())
g.set(xlabel=None)
g.set_titles("{row_name} - {col_name}")
g.fig.subplots_adjust(bottom=0.2)
plt.show()


#####################
# Plot the data
sns.set_style('whitegrid')
g = sns.FacetGrid(data=world_filtered, row='VisaType', col='countries2', hue='datetype', height=3.5, aspect=1.2, sharey=False)
g = g.map(plt.plot, 'date', 'delay_days', marker='o', markersize=4, linestyle='', alpha=0.7)
g = g.set_titles(row_template='{row_name}', col_template='{col_name}')
g = g.set_xlabels('Date').set_ylabels('Delay Days')
g = g.set_xticklabels(rotation=90)
g = g.set(xlim=(world_filtered['date'].min()-10, world_filtered['date'].max())+10)
g = g.add_legend(title='Date Type', bbox_to_anchor=(1, 1))
# Set different y-axis limits for the first row of plots
for ax in g.axes[0]:
    ax.set_ylim(-10, 600)
plt.show()


