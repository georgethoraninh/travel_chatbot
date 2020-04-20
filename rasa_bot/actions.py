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
    iata = airport_df[airport_df['City']==location]['IATA'].iloc[0] 
    return iata

def format_date(extracted_date):
    '''
    Converts the date to the format: YYYY-MM-DD 
    Returns result as a string.
    '''
    formatted_date = parser.parse(extracted_date).strftime('%Y-%m-%d')
    return formatted_date

def _find_flight_offer(origin: Text, destination: Text, depart_date: Text, return_date: Text, budget: Text) -> List[Dict]:
    
    '''Returns json of flight offer matching the search criteria'''

    # Retrieves the proper IATA airport codes from the corresponding location
    origin_iata = location_to_iata(origin)
    destination_iata = location_to_iata(destination)

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
                                    max = '1' # Set the limit of results returned
                                    )
    #print(origin_iata,destination_iata,depart_date,return_date,extracted_price[0])
    return response
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
        # return {
        #     "cuisine": self.from_entity(entity="cuisine", not_intent="chitchat"),
        #     "num_people": [
        #         self.from_entity(
        #             entity="number", intent=["inform", "request_restaurant"]
        #         ),
        #     ],
        #     "outdoor_seating": [
        #         self.from_entity(entity="seating"),
        #         self.from_intent(intent="affirm", value=True),
        #         self.from_intent(intent="deny", value=False),
        #     ],
        #     "preferences": [
        #         self.from_intent(intent="deny", value="no additional preferences"),
        #         self.from_text(not_intent="affirm"),
        #     ],
        #     "feedback": [self.from_entity(entity="feedback"), self.from_text()],
        # }
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

        flight_offer = _find_flight_offer(origin, destination, depart_date, return_date, budget)

        # utter submit template
        dispatcher.utter_message(text=tracker.get_slot("destination"))
        dispatcher.utter_message(text=tracker.get_slot("origin"))
        dispatcher.utter_message(text=tracker.get_slot("depart_date"))
        dispatcher.utter_message(text=tracker.get_slot("return_date"))
        dispatcher.utter_message(text=tracker.get_slot("budget"))
        dispatcher.utter_message(template="utter_submit")
        return []

