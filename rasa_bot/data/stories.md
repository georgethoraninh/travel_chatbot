
## happy path
* greet
    - utter_greet
* request_flight
    - flight_form
    - form{"name": "flight_form"}
    - form{"name": null}
* affirm
    - utter_ask_more_help
* deny
    - utter_noworries
    
## chitchat stop but continue path
* request_flight
    - flight_form
    - form{"name": "flight_form"}
* chitchat
    - utter_chitchat
    - flight_form
* stop
    - utter_ask_continue
* affirm
    - flight_form
    - form{"name": null}
    - utter_slots_values
* thankyou
    - utter_noworries

## bot challenge
* bot_challenge
  - utter_iamabot

## interactive_story_1
* greet
    - utter_greet
* request_flight
    - flight_form
    - form{"name": "flight_form"}
    - slot{"requested_slot": "destination"}
* form: inform{"destination": "new york"}
    - form: flight_form
    - slot{"destination": "new york"}
    - slot{"requested_slot": "origin"}
* form: inform{"origin": "toronto"}
    - form: flight_form
    - slot{"origin": "toronto"}
    - slot{"requested_slot": "depart_date"}
* form: inform{"depart_date": "aug 10"}
    - form: flight_form
    - slot{"depart_date": "aug 10"}
    - slot{"requested_slot": "return_date"}
* form: inform{"return_date": "aug 24"}
    - form: flight_form
    - slot{"return_date": "aug 24"}
    - slot{"requested_slot": "budget"}
* form: inform{"budget": "800"}
    - form: flight_form
    - slot{"budget": "800"}
    - form{"name": null}
    - slot{"requested_slot": null}
* affirm
    - utter_ask_more_help
* deny
    - utter_noworries
