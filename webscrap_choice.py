import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random
import time
import os
from datetime import datetime, date, timezone

# Base URL pattern
base_url = 'https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/when-to-file-your-adjustment-of-status-application-for-family-sponsored-or-employment-based'
suffix_url = 'https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/when-to-file-your-adjustment-of-status-application-for-family-sponsored-or-employment-based-{}'

# Create an empty list to hold data
data = []

# Loop through URL pattern from 1 to 2
for i in range(0, 10):
    # Handle the base URL without suffix
    if i == 0:
        url = base_url
    else:
        url = suffix_url.format(i)
    print(url)

    timeout = random.randint(3, 30)
    print(f"Accessing URL: {url} (timeout: {timeout} seconds)")
    time.sleep(timeout)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    element = soup.select_one('#block-uscis-design-content article > div:nth-of-type(1) > div > div > p:nth-of-type(6) > strong')
# //*[@id="block-uscis-design-content"]/article/div[1]/div/div/p[7]/strong
# //*[@id="block-uscis-design-content"]/article/div[1]/div/div/h3[2]
    # Print the text of the element if found
    if element:
        print(element.get_text())
    else:
        print("Element not found")
    
    # # Extract date from h2 tag
    # date = soup.find('h2').get_text() if soup.find('h2') else 'N/A'
    
    # # Extract information from tables
    # tables = soup.find_all('table')
    # for table in tables:
    #     captions = table.find_all('caption')
    #     for caption in captions:
    #         caption_text = caption.get_text()
    #         if 'Dates for Filing for Employment-Based Adjustment of Status Applications' in caption_text:
    #             data.append({'URL': url, 'Date': date, 'Type': 'Dates for Filing', 'Caption': caption_text})
    #         elif 'Final Action Dates for Employment-Based Adjustment of Status Applications' in caption_text:
    #             data.append({'URL': url, 'Date': date, 'Type': 'Final Action', 'Caption': caption_text})

# Create a DataFrame
df = pd.DataFrame(data)

# # Save DataFrame to a CSV file
# df.to_csv('uscis_dates.csv', index=False)

# print('Data saved to uscis_dates.csv')


