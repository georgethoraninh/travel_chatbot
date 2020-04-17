"""

Travel Chat Bot for Slack
title:  amadeus_query.py
author: George Thoraninh
usage:  python amadeus_query.py

"""
# import statements
import warnings
warnings.filterwarnings('ignore')
import os
import requests
from amadeus import Client, ResponseError, Location
from functools import lru_cache
import time
from datetime import datetime
from dateutil import parser

import pandas as pd
import numpy as np
import pprint as pp
import json
from pandas.io.json import json_normalize
import re
from timeit import default_timer
from  more_itertools import unique_everseen

# NER
import nltk
import spacy
import pprint as pprint
import en_core_web_sm # CNN gets loaded in, sees what words depends on each other, POS tagging, entity recognition 
from spacy import displacy # Visualize NER

from slackeventsapi import SlackEventAdapter
from slack import WebClient
import ssl

# Chatterbot
# from chatterbot import ChatBot
# from chatterbot.trainers import ListTrainer

# Amadeus variables
amadeus_api_key = os.environ['AMADEUS_API_KEY']
amadeus_api_secret = os.environ['AMADEUS_API_SECRET']


auth_response = requests.post('https://api.amadeus.com/v1/security/oauth2/token',
                              data={'grant_type': 'client_credentials',
                                    'client_id': amadeus_api_key,
                                    'client_secret': amadeus_api_secret})
bearer = auth_response.json()['access_token']
#print(bearer)

# Slack variables

# Used to help verify security certificate
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_bot_id = os.environ['SLACK_BOT_ID']
# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a Slack WebClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(token = slack_bot_token,
                         ssl=ssl_context)


# Airport codes
airport_df = pd.read_csv('clean_airports.csv')

convo_1  = [['I want to go from Toronto to New York from August 1 to August 15. My budget is $800']]


##################### 
# Text Preprocessing 
##################### 

# Preprocess frames data set using functions above 
def data_preprocess(text_data):
  list_of_convo = text_to_convo(text_data) 
  list_of_statement = convo_to_statement(list_of_convo)
  return list_of_statement

# Preprocess a conversation using all functions above
def convo_preprocess(conversation):
  flat_convo = flatten_list(conversation)
  list_user_statement = extract_user_statement(flat_convo)
  return list_user_statement

# Helper functions

# Splits text data into separate lists for each conversation
def text_to_convo(text):
  list_convos = [convo.split('\n') for convo in text.split('*') if text]         # Conversation delimited by *
  list_convos = [convo for convo in list_convos if convo != ['']]                # Remove empty conversation
  return list_convos

# Splits all the statements from a conversation into their own string
def convo_to_statement(list_convos):
  sep_convos = []
  for items in list_convos: 
    sep_convos.append([])                     # Creates list for each conversation
    for item in items:
      item = item.split('\\n')                # Splits conversations into statements 
      sep_convos[-1].append(item)             # Adds all statements to corresponding list
  return sep_convos

# Flattens the list as there is a list in another list
# - Handles sentence tokenization, as all statements are separated into their own string in this list 
def flatten_list(conversation): 
  flat_list = []
  for sublist in conversation:
    for item in sublist:
          flat_list.append(item)
  return flat_list

# Extracts only the users' statements from the conversations
def extract_user_statement(conversation):
  user_statement = conversation[0::2] 
  return user_statement  

########### 
# NER 
########### 

# English multi-task CNN trained on OntoNotes. Assigns context-specific token vectors, POS tags, dependency parse and named entities
def ner_model(sample_conversation):
  nlp = en_core_web_sm.load()
  text = ' '.join(sample_conversation)
  convo_nlp = nlp(text)
  return convo_nlp

# Extracts locations from NER model
def extract_location_ner(nlp_doc):
  gpe_list = []
  for entity in nlp_doc.ents:
    if entity.label_ == 'GPE':      #GPE -> Countries, cities, states
      gpe_list.append(entity.text)
      
  return list(unique_everseen(gpe_list))

# Extracts dates from NER model 
def extract_date_ner(nlp_doc):
  date_list = []
  for entity in nlp_doc.ents:
    if entity.label_ == 'DATE':      #DATE -> Absolute or relative dates or periods
      date_list.append(entity.text)
      
  return date_list

# Extracts dates from NER model 
def extract_price_ner(nlp_doc):
  price_list = []
  for entity in nlp_doc.ents:
    if entity.label_ == 'MONEY':      #Money -> Monetary values, including unit
      price_list.append(entity.text)
    elif entity.label == 'CARDINAL':
      price_list.append(entity.text)
  return price_list

# might take out
def ner_ouput(location_list,date_list,price_list):
  output = {'Locations':location_list,
            'Dates':date_list,
            'Price':price_list}
  return output

########### 
# Amadeus 
########### 

def location_to_iata(extracted_location):
  '''
  Converts the city location to airport code 
  used for API call. 
  Returns results as a tuple.
  '''
  origin_place = extracted_location[0] #Fix: parse better, multiple locations?
  destination_place = extracted_location[1]

  origin_iata = airport_df[airport_df['City']==origin_place]['IATA'].iloc[0] # Fix: lower/upper case
  destination_iata = airport_df[airport_df['City']==destination_place]['IATA'].iloc[0]
  return origin_iata, destination_iata #

def format_date(extracted_date):
  '''
  Converts the date to the format: YYYY-MM-DD 
  Returns results as a tuple.
  '''
  date_string = extracted_date[0]
  date_list = date_string.split('to') # Fix: other date inputs
  datetime_depart = parser.parse(date_list[0]).strftime('%Y-%m-%d')
  datetime_return = parser.parse(date_list[1]).strftime('%Y-%m-%d')
  return datetime_depart, datetime_return 

def flight_offer_get(extracted_location, extracted_date, extracted_price):
  
  # Retrieves the necessary location information
  iata_tuple = location_to_iata(extracted_location)
  origin_iata = iata_tuple[0]
  destination_iata = iata_tuple[1]

  # Retrieves the necessary date information
  date_tuple = format_date(extracted_date)
  depart_date = date_tuple[0]
  return_date = date_tuple[1]

  response = call_api('/shopping/flight-offers',
                  origin = origin_iata,
                  destination = destination_iata,
                  departureDate = depart_date,
                  returnDate = return_date,
                  adults = '1', # Set ticket search for one adult
                  nonStop = 'true', # Returns tickets that have no stops
                  currency = 'CAD', # Set currency as CAD 
                  maxPrice = extracted_price[0],
                  max = '5' # Set the limit of results returned
                  )
  #print(origin_iata,destination_iata,depart_date,return_date,extracted_price[0])
  return response

# API has quotas, so better to cache everything
@lru_cache(maxsize=2048)
def call_api(url, **params):
    full_url = f'https://api.amadeus.com/v1{url}'
    response = requests.get(full_url,
                            params=params,
                            headers={'Authorization': f'Bearer {bearer}',
                                     'Content-Type': 'application/vnd.amadeus+json'})
    return response.json()

# Converts a list to dict; removal is an integer to delimit the square brackets
def list_to_dict(list_to_convert, removal):
    converted_dict = json.loads(str(list_to_convert)[removal:-removal].replace('\'','\"')) 
    return converted_dict

def flight_offer_response(response, extracted_location):

    offer_list = []
    num_offer = 0
    # every offer form the response
    iata_code = [*response['dictionaries']['locations'].keys()] #gets a list of airport codes

    for offer in response['data']:
        # Converted to string so we can get rid of square brackets [], then replaced by 
        services_dict = list_to_dict(offer['offerItems'],1)
        price = services_dict['price']['total']
        depart_flight_dict = list_to_dict([*services_dict['services'][0].values()], 2)
        arrive_flight_dict = list_to_dict([*services_dict['services'][1].values()], 2)
        num_ticket_avail = depart_flight_dict['pricingDetailPerAdult']['availability']
        # depart time - needs parsing 
        depart_time = depart_flight_dict['flightSegment']['departure']['at']
        arrival_time = depart_flight_dict['flightSegment']['arrival']['at']
        trip_duration = depart_flight_dict['flightSegment']['duration']
        flight_carrier = depart_flight_dict['flightSegment']['carrierCode']
        for key, value in response['dictionaries']['carriers'].items():
            if flight_carrier == key:
                flight_carrier_str = value

        # crafting response for user
        num_offer+=1
        response_str = 'Flight Offer ' + str(num_offer) + ': ' + extracted_location[0] + ' (' + iata_code[0] + ') --> ' + extracted_location[1] +  ' (' + iata_code[1] + ')\nDeparting at: ' + depart_time + '\nArriving at: ' + arrival_time + '\nTrip Duration: ' + trip_duration + '\nFlight Carrier: ' + flight_carrier_str + '\nPrice: $' + price + ' CAD\n' + str(num_ticket_avail) + ' tickets left!'
        
        offer_list.append(response_str)
        
    return offer_list

@slack_events_adapter.on('message')
def handle_message(event_data):
  '''
  Handles Slack messages
  '''
  message = event_data['event']

  if message['user'] != slack_bot_id:
      user_message = message.get('text')
      channel = message['channel']
      if 'hi' in user_message:
          response = 'Hello <@%s>! :tada:' % message['user']
  
          slack_client.chat_postMessage(channel=channel,text=response)
#######
# MAIN
#######

# Preprocessing
sample_convo = convo_preprocess(convo_1)
pp.pprint(convo_1)
print('\n')
# Applying preprocessed text to NER
nlp_doc = ner_model(sample_convo)

# Extracting information from NER model
extracted_location = extract_location_ner(nlp_doc)
extracted_date = extract_date_ner(nlp_doc)
extracted_price = extract_price_ner(nlp_doc)

#ner_ouput(extracted_location, extracted_date, extracted_price) #might not need

response = flight_offer_get(extracted_location, extracted_date, extracted_price)

flight_offer_list = flight_offer_response(response, extracted_location)

print(*flight_offer_list, sep='\n\n')

# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
if __name__=="__main__":
    slack_events_adapter.start(port=3000)