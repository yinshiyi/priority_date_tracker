import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date, time, timezone
import matplotlib.ticker as ticker

most_recent = pd.read_csv('data/2024-06-12_20-20-10_rawdata_world.csv')
#this table is the 2016-2022 table summary
previous = pd.read_csv('data/2024-06-13_09-59-17_rawdata_world.csv')
world_merged_table = pd.concat([most_recent, previous])
world_merged_table['date'] = pd.to_datetime(world_merged_table['date']).dt.strftime('%y-%m')

choice = pd.read_csv('uscis_dates.csv',na_values=['N/A'])
choice['date'] = pd.to_datetime(choice['date'], errors='coerce').dt.strftime('%y-%m')
choice['datetype'] = np.where(choice['Element Text'].str.contains('Final', na=False), 'Final Action Date',
                              np.where(choice['Element Text'].notna(), 'Priority Date', pd.NA))
clean_choice = choice.drop(columns=['Element Text','URL'])

merged_table_china = (world_merged_table
                .query("datetype == 'Final Action Date' or datetype == 'Priority Date'")
                .query("VisaType in ['1st'] and countries.str.contains('CHINA')")
                .assign(category=lambda df: df['VisaType'] + ' ' + df['datetype'].str.split().str[0] + ' ' + df['datetype'].str.split().str[-1])
                .sort_values('date', ascending=True)
                .reset_index(drop=True)
                )

clean_china = merged_table_china.drop(columns=['VisaType','countries', 'date_gov','delay'])

merged_data = pd.merge(clean_china, clean_choice, on='date', how='left')
filtered_data = merged_data[(merged_data['datetype_y'].isna()) | (merged_data['datetype_x'] == merged_data['datetype_y'])]

ax = sns.scatterplot(data=filtered_data, x='date', y='delay_days', hue='category')
ax.xaxis.set_major_locator(ticker.MultipleLocator(12))

ax = sns.scatterplot(data=clean_china, x='date', y='delay_days', hue='category')
ax.xaxis.set_major_locator(ticker.MultipleLocator(12))
