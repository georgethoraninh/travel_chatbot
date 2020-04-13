"""

Travel Chat Bot for Slack
title:  amadeus_query.py
author: George Thoraninh
usage:  python amadeus_query.py

"""
# import statements
import os
import ssl
from amadeus import Client, ResponseError, Location

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

amadeus_api_key = os.environ['AMADEUS_API_KEY']
amadeus_api_secret = os.environ['AMADEUS_API_SECRET']

# initilize amadeus client
amadeus = Client(
    client_id = amadeus_api_key,
    client_secret = amadeus_api_secret,
    ssl = ssl_context
)

response = amadeus.reference_data.locations.airports.get(longitude=0.1278, latitude=51.5074)

print(response.data)