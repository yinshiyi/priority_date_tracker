# //*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div[1]
import requests
from datetime import datetime
import os
import pandas as pd

with open('/Users/yins/side/priority_date_tracker/api.key', 'r') as f:
    api_key = f.read().strip()
origin = '2560 Orchard Pkwy, San Jose, CA 95131'
destination = '845 N Humboldt St, San Mateo, CA 94401'


url1 = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&traffic_model=best_guess&departure_time=now&key={api_key}'
url2 = f'https://maps.googleapis.com/maps/api/directions/json?origin={destination}&destination={origin}&traffic_model=best_guess&departure_time=now&key={api_key}'

response1 = requests.get(url1)
response2 = requests.get(url2)

data1 = response1.json()
data2 = response2.json()

duration1 = data1['routes'][0]['legs'][0]['duration_in_traffic']['text']
duration2 = data2['routes'][0]['legs'][0]['duration_in_traffic']['text']

print(f"to home: {duration1}")
print(f"to work: {duration2}")

data = {
    'Date': [datetime.now()],
    'Home': [duration1],
    'Work': [duration2],
}
 
# Make data frame of above data
df = pd.DataFrame(data)

# today = datetime.datetime.now()
datapath = '/Users/yins/side/priority_date_tracker/mapdata/'
if not os.path.exists(datapath):
    os.mkdir(datapath)
filename = 'log.csv'
filepath = datapath+filename

# append data frame to CSV file
df.to_csv(filepath, mode='a', index=False, header=False)
