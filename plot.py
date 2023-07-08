import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data for plotting
merged_table = pd.read_csv('data/<filename>.csv')
world_merged_table = pd.read_csv('data/<filename>_world.csv')

# Perform the necessary data transformations and create the plots
# ...

# Plotting code goes here
# ...

# create the 4 line plots with legends
ax = sns.lineplot(data=merged_table, x='date', y='delay_days', hue='category')
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

# create the country line plots with legends 
ax.sns.lineplot(data=finaldate.loc[finaldate['VisaType'] == '1st'], x='date', y='delay_days', hue='countries2',style='countries2', alpha=0.5,linewidth=5)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

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