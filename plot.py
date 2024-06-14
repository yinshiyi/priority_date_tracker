import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date, time, timezone
import matplotlib.ticker as ticker

# Load the data for plotting
# read in todays date, and load the most recent csv in the data folder, out put figure as relvent name but include time stamp in the actual figure
most_recent = pd.read_csv('data/2024-06-12_20-20-10_rawdata_world.csv')
#this table is the 2016-2022 table summary
previous = pd.read_csv('data/2024-06-13_09-59-17_rawdata_world.csv')
world_merged_table = pd.concat([most_recent, previous])
world_merged_table['date'] = pd.to_datetime(world_merged_table['date']).dt.strftime('%y-%m')

######################################################


merged_table_china = (world_merged_table
                .query("datetype == 'Final Action Date' or datetype == 'Priority Date'")
                .query("VisaType in ['1st', '2nd'] and countries.str.contains('CHINA')")
                .assign(category=lambda df: df['VisaType'] + ' ' + df['datetype'].str.split().str[0] + ' ' + df['datetype'].str.split().str[-1])
                .sort_values('date', ascending=True)
                .reset_index(drop=True)
                )
merged_table_india = (world_merged_table
                .query("datetype == 'Final Action Date' or datetype == 'Priority Date'")
                .query("VisaType in ['1st', '2nd'] and countries.str.contains('INDIA')")
                .assign(category=lambda df: df['VisaType'] + ' ' + df['datetype'].str.split().str[0] + ' ' + df['datetype'].str.split().str[-1])
                .sort_values('date', ascending=True)
                .reset_index(drop=True)
                )
finaldate = (world_merged_table
             .query("datetype == 'Final Action Date' and VisaType == '1st'")
             .query("~countries.str.contains('HONDURAS')")
             .sort_values(['date', 'countries'], ascending=[True, True])
             .reset_index(drop=True)
             )

# Perform the necessary data transformations and create the plots
# ...

# timestamp
today = datetime.now()
timestamp = today.strftime("%Y-%m-%d_%H-%M-%S")

# Plotting code goes here
# ...

# create the 4 line plots with legends for China my fav
# plt.figure(figsize=(24, 6))
ax = sns.lineplot(data=merged_table_china, x='date', y='delay_days', hue='category')
ax.xaxis.set_major_locator(ticker.MultipleLocator(12))
ax.set_title('EBs delay for China')
# plt.savefig(f'plot_china_{timestamp}.png')

ax = sns.lineplot(data=merged_table_india, x='date', y='delay_days', hue='category')
ax.xaxis.set_major_locator(ticker.MultipleLocator(3))

# create the country line plots with legends, world plot for EB1
ax = sns.lineplot(data=finaldate, x='date', y='delay_days', hue='countries',style='countries', alpha=0.8,linewidth=5)
plt.draw()
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
########################
# more work is needed
# facet plot for consulting, countries2 is short string versions
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