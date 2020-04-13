"""

Travel Chat Bot for Slack
title:  skyscanner_query.py
author: George Thoraninh
usage:  python skyscanner_query.py

"""
# import statements
import os
import requests
from skyscanner.skyscanner import Flights

sky_api_key = os.environ['SKYSCANNER_API_KEY']

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/CA/CAD/en-US/AYGA-sky/AYMD-sky/2020-09-01"

querystring = {"inboundpartialdate":"2020-10-01"}

headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': sky_api_key
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)




# flights_service = Flights('2ebdebb98amsh706c9ef4215caf9p1c2f8djsn541d0b6d9982')
# result = flights_service.get_result(
#     country='UK',
#     currency='GBP',
#     locale='en-GB',
#     originplace='SIN-sky',
#     destinationplace='KUL-sky',
#     outbounddate='2020-05-28',
#     inbounddate='2020-05-31').parsed

# print(result)