"""

Travel Chat Bot for Slack
title:  skyscanner_query.py
author: George Thoraninh
usage:  python skyscanner_query.py

"""
# import statements

import requests

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/CA/CAD/en-US/AYGA-sky/AYMD-sky/2020-09-01"

querystring = {"inboundpartialdate":"2020-10-01"}

headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': "d3a270537fmsh197257bc46f605bp13894cjsn011a2fd14858"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)