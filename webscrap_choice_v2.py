import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random
import time
import os
from datetime import datetime, date, timezone

# Function to extract text from an element if it exists
def get_element_text(soup, selector):
    element = soup.select_one(selector)
    return element.get_text().strip() if element else 'N/A'

df = pd.DataFrame(columns=['date', 'Element Text', 'URL'])  # Assuming these are your column names

# Base URL pattern
base_url = 'https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/when-to-file-your-adjustment-of-status-application-for-family-sponsored-or-employment-based'
suffix_url = 'https://www.uscis.gov/green-card/green-card-processes-and-procedures/visa-availability-priority-dates/when-to-file-your-adjustment-of-status-application-for-family-sponsored-or-employment-based-{}'

numbers = [i for i in range(-1, 0) if i != 18]

# Loop through URL pattern from 1 to 2
for i in numbers:
    # Handle the base URL without suffix
    if i == -1:
        url = base_url
    else:
        url = suffix_url.format(i)
    print(url)

    timeout = random.randint(3, 30)
    print(f"Accessing URL: {url} (timeout: {timeout} seconds)")
    time.sleep(timeout)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # //*[@id="block-uscis-design-content"]/article/div[1]/h1/span
    # Extract date from h3[2] tag
    date_selector_1 = '#block-uscis-design-content article > div:nth-of-type(1) > h1 > span'
    date_string = get_element_text(soup, date_selector_1)
    colon_index = date_string.rfind(':')
    date = date_string[colon_index + 2:] 

    # If the first selector fails, try the second one
    if date == 'N/A':
        date_selector_2 = '#block-uscis-design-content article > div:nth-of-type(1) > div > div > h3'
        date = get_element_text(soup, date_selector_2)
    
    # Try the first selector for strong text
    strong_text_selector_1 = '#block-uscis-design-content article > div:nth-of-type(1) > div > div > p:nth-of-type(6) > strong'
    element_text = get_element_text(soup, strong_text_selector_1)
    
    # If the first selector fails, try the second one
    if element_text == 'N/A':
        strong_text_selector_2 = '#block-uscis-design-content article > div:nth-of-type(1) > div > div > p:nth-of-type(7) > strong'
        element_text = get_element_text(soup, strong_text_selector_2)
    
    # Append the data to the list
    new_row = {'date': date, 'Element Text': element_text, 'URL': url}
    df.loc[len(df)] = new_row

# Save DataFrame to a CSV file
# df.to_csv('uscis_dates2.csv', index=False, mode='a', header=not os.path.exists('uscis_dates.csv'))
df.to_csv('uscis_dates2.csv', index=False)
print('Data saved to uscis_dates.csv')
