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
airport_df = pd.read_csv('clean_airports.csv')

def location_to_iata(extracted_location):
    '''
    Converts the city location to airport code used for API call. 
    Returns result as a string.
    '''
    iata = airport_df[airport_df['City']==extracted_location]['IATA'].iloc[0] 
    return iata

def format_date(extracted_date):
    '''
    Converts the date to the format: YYYY-MM-DD 
    Returns result as a string.
    '''
    formatted_date = parser.parse(extracted_date).strftime('%Y-%m-%d')
    return formatted_date

# Converts a list to dict; removal is an integer to delimit the square brackets
def list_to_dict(list_to_convert, removal):
    '''
    Converts a list to dict.
    Removal is an integer to delimit the square brackets.
    '''
    converted_dict = json.loads(str(list_to_convert)[removal:-removal].replace('\'','\"')) 
    return converted_dict

# API has quotas, so better to cache everything
@lru_cache(maxsize=2048)
def call_api(url, **params):
    full_url = f'https://api.amadeus.com/v1{url}'
    response = requests.get(full_url,
                                                    params=params,
                                                    headers={'Authorization': f'Bearer {bearer}',
                                                                     'Content-Type': 'application/vnd.amadeus+json'})
    return response.json()

def _find_flight_offer(origin: Text, destination: Text, depart_date: Text, return_date: Text, budget: Text) -> List[Dict]:
    
    '''Returns json of flight offer matching the search criteria'''

    # Retrieves the proper IATA airport codes from the corresponding location
    origin_iata = location_to_iata(origin)
    destination_iata = location_to_iata(destination)

    # Converts date to proper format 
    formatted_depart_date = format_date(depart_date)
    formatted_return_date = format_date(return_date)

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

        iata_code = list(flight_offer_json['dictionaries']['locations'].keys())
        
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
            # depart time - needs parsing 
            depart_time = depart_flight_dict['flightSegment']['departure']['at']
            arrival_time = depart_flight_dict['flightSegment']['arrival']['at']
            trip_duration = depart_flight_dict['flightSegment']['duration']
            flight_carrier = depart_flight_dict['flightSegment']['carrierCode']
            for key, value in flight_offer_json['dictionaries']['carriers'].items():
                    if flight_carrier == key:
                            flight_carrier_str = value

            # crafting response for user
            num_offer+=1
            # response_str = 'Flight Offer ' + str(num_offer) + ': ' + extracted_location[0] + ' (' + iata_code[0] + ') --> ' + extracted_location[1] +  ' (' + iata_code[1] + ')\nDeparting at: ' + depart_time + '\nArriving at: ' + arrival_time + '\nTrip Duration: ' + trip_duration + '\nFlight Carrier: ' + flight_carrier_str + '\nPrice: $' + price + ' CAD\n' + str(num_ticket_avail) + ' tickets left!'
            response_str = (f'Your flight from {origin} ({iata_code[0]}) to {destination} ({iata_code[1]}) would be with {flight_carrier_str} and cost ${price} CAD, from {depart_time} to {arrival_time}. Is that okay?')
            offer_list.append(response_str)
        
        response = '\n'.join(offer_list)

        # Utter response message to user
        dispatcher.utter_message(text=response)
        return []

