"""

Travel Chat Bot for Slack
title:  amadeus_query.py
author: George Thoraninh
usage:  python amadeus_query.py

"""
# import statements
import os
import ssl
import requests
from amadeus import Client, ResponseError, Location
from functools import lru_cache





########### 
# Amadeus #
########### 
amadeus_api_key = os.environ['AMADEUS_API_KEY']
amadeus_api_secret = os.environ['AMADEUS_API_SECRET']


auth_response = requests.post('https://api.amadeus.com/v1/security/oauth2/token',
                              data={'grant_type': 'client_credentials',
                                    'client_id': amadeus_api_key,
                                    'client_secret': amadeus_api_secret})
bearer = auth_response.json()['access_token']
#print(bearer)
# API has quotas, so better to cache everything
@lru_cache(maxsize=2048)
def call_api(url, **params):
    full_url = f'https://api.amadeus.com/v1{url}'
    response = requests.get(full_url,
                            params=params,
                            headers={'Authorization': f'Bearer {bearer}',
                                     'Content-Type': 'application/vnd.amadeus+json'})
    return response.json()

response = call_api('/shopping/flight-offers',
                origin='YYZ',
                destination='JFK',
                departureDate='2020-08-01',
                returnDate='2020-08-15',
                adults='1',
                nonStop='true',
                currency='CAD',
                maxPrice='1000',
                max='5'
                )
print(response.keys())

print('*******')

print(response.values())