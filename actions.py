from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

import os
import requests
from amadeus import Client, ResponseError, Location
from functools import lru_cache
import time
from datetime import datetime
from dateutil import parser
import pandas as pd
import json


# Amadeus variables
amadeus_api_key = os.environ['AMADEUS_API_KEY']
amadeus_api_secret = os.environ['AMADEUS_API_SECRET']
auth_response = requests.post('https://api.amadeus.com/v1/security/oauth2/token',
                                                            data={'grant_type': 'client_credentials',
                                                                        'client_id': amadeus_api_key,
                                                                        'client_secret': amadeus_api_secret})
bearer = auth_response.json()['access_token']

# Airport codes
airport_df = pd.read_csv('csv_files/clean_airports.csv')

def location_to_iata(extracted_location):
    '''
    Converts the city location to airport code used for API call. 
    Returns result as a string.
    '''
    iata = airport_df[airport_df['City']==extracted_location]['IATA'].iloc[0] 
    return iata

def parse_date(extracted_date):
    '''
    Converts the date to the format: YYYY-MM-DD 
    Returns result as a string.
    '''
    formatted_date = parser.parse(extracted_date).strftime('%Y-%m-%d')
    return formatted_date

def list_to_dict(list_to_convert, removal):
    '''
    Converts a list to dict.
    Removal is an integer to delimit the square brackets.
    Returns a dict.
    '''
    converted_dict = json.loads(str(list_to_convert)[removal:-removal].replace('\'','\"')) 
    return converted_dict

def format_time(time_string):
    '''
    Converts a string to time.
    Returns a string with proper format.
    '''
    formatted_time = datetime.strptime(time_string[0:-9], '%Y-%m-%dT%H:%M').time()
    formatted_time = formatted_time.strftime('%I:%M%p')
    return formatted_time

def format_date(date_string):
    '''
    Converts a string to date.
    Returns a string with proper format.
    '''
    formatted_date = datetime.strptime(date_string[0:-9], '%Y-%m-%dT%H:%M').date()
    formatted_date = formatted_date.strftime('%b %d %Y')
    return formatted_date

# API has quotas, so better to cache everything
@lru_cache(maxsize=2048)
def call_api(url, **params):
    full_url = f'https://api.amadeus.com/v1{url}'
    response = requests.get(full_url,
                            params=params,
                            headers={'Authorization': f'Bearer {bearer}','Content-Type': 'application/vnd.amadeus+json'})
    return response.json()

def _find_flight_offer(origin: Text, destination: Text, depart_date: Text, return_date: Text, budget: Text) -> List[Dict]:
    
    '''Returns json of flight offer matching the search criteria'''

    # Retrieves the proper IATA airport codes from the corresponding location
    origin_iata = location_to_iata(origin)
    destination_iata = location_to_iata(destination)

    # Converts date to proper format 
    formatted_depart_date = parse_date(depart_date)
    formatted_return_date = parse_date(return_date)

    # Removes $ sign if associated with budget
    budget = budget.replace('$','')

    response = call_api('/shopping/flight-offers',
                        origin = origin_iata,
                        destination = destination_iata,
                        departureDate = formatted_depart_date,
                        returnDate = formatted_return_date,
                        adults = '1', # Set ticket search for one adult
                        nonStop = 'true', # Returns tickets that have no stops
                        currency = 'CAD', # Set currency as CAD 
                        maxPrice = budget, # Future: validate 
                        max = '1' # Set the limit of results returned
                        )
    #print(origin_iata,destination_iata,depart_date,return_date,extracted_price[0])
    return response

class FlighttForm(FormAction):

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "flight_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["destination", "origin", "depart_date", "return_date", "budget"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "destination": self.from_entity(entity="destination", intent="inform"),
            "origin": self.from_entity(entity="origin", intent="inform"),
            "depart_date": self.from_entity(entity="depart_date", intent="inform"),
            "return_date": self.from_entity(entity="return_date", intent="inform"),
            "budget": self.from_entity(entity="budget", intent="inform"),
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        destination = tracker.get_slot("destination")
        origin = tracker.get_slot("origin")
        depart_date = tracker.get_slot("depart_date")
        return_date = tracker.get_slot("return_date")
        budget = tracker.get_slot("budget")

        offer_list = []
        num_offer = 0

        flight_offer_json = _find_flight_offer(origin, destination, depart_date, return_date, budget)

        # Capitlized the first letter of every word in the location
        origin = origin.title()
        destination = destination.title()

        # If we want more than one flight offer
        for offer in flight_offer_json['data']:
            # Converted to string so we can get rid of square brackets [], then replaced by 
            services_dict = list_to_dict(offer['offerItems'],1)
            price = services_dict['price']['total']
            depart_flight_dict = list_to_dict([*services_dict['services'][0].values()], 2)
            arrive_flight_dict = list_to_dict([*services_dict['services'][1].values()], 2)
            num_ticket_avail = depart_flight_dict['pricingDetailPerAdult']['availability']

            # Departing flight segment
            depart_time_depart = format_time(depart_flight_dict['flightSegment']['departure']['at'])
            depart_date_depart = format_date(depart_flight_dict['flightSegment']['departure']['at'])

            arrival_time_depart = format_time(depart_flight_dict['flightSegment']['arrival']['at'])
            arrival_date_depart = format_date(depart_flight_dict['flightSegment']['arrival']['at'])


            # Returning flight segment
            depart_time_return = format_time(arrive_flight_dict['flightSegment']['departure']['at'])
            depart_date_return = format_date(arrive_flight_dict['flightSegment']['departure']['at'])

            arrival_time_return = format_time(arrive_flight_dict['flightSegment']['arrival']['at'])
            arrival_date_return = format_date(arrive_flight_dict['flightSegment']['arrival']['at'])


            depart_iata = depart_flight_dict['flightSegment']['departure']['iataCode']
            arrival_iata = depart_flight_dict['flightSegment']['arrival']['iataCode']

            trip_duration = depart_flight_dict['flightSegment']['duration']
            flight_carrier = depart_flight_dict['flightSegment']['carrierCode']

            for key, value in flight_offer_json['dictionaries']['carriers'].items():
                    if flight_carrier == key:
                            flight_carrier_str = value

            num_offer+=1

            # Response for user
            response_str = (f'There\'s a flight to {destination} ({arrival_iata}) with {flight_carrier_str} that cost ${price} CAD. It\'d be from {depart_date_depart} {depart_time_depart} to {arrival_date_depart} {arrival_time_depart}. You will return to {origin} ({depart_iata}) on a flight at {depart_date_return} {depart_time_return} to {arrival_date_return} {arrival_time_return}. Is that okay?')
            
            offer_list.append(response_str)
        
        response = '\n'.join(offer_list)

        # Utter response message to user
        dispatcher.utter_message(text=response)
        return []

