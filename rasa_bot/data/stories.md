
## happy path
* greet
    - utter_greet
* request_flight
    - flight_form
    - form{"name": "flight_form"}
    - form{"name": null}
    - utter_slots_values
* thankyou
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
* form: inform{"destination": "Tokyo"}
    - form: flight_form
    - slot{"destination": "Tokyo"}
    - slot{"requested_slot": "origin"}
* form: inform{"origin": "Toronto"}
    - form: flight_form
    - slot{"origin": "Toronto"}
    - slot{"requested_slot": "depart_date"}
* form: inform{"depart_date": "May 10"}
    - form: flight_form
    - slot{"depart_date": "May 10"}
    - slot{"requested_slot": "return_date"}
* form: inform{"return_date": "May 24"}
    - form: flight_form
    - slot{"return_date": "May 24"}
    - slot{"requested_slot": "budget"}
* form: inform{"budget": "2000"}
    - form: flight_form
    - slot{"budget": "2000"}
    - form{"name": null}
    - slot{"requested_slot": null}
    - utter_slots_values
* thankyou
    - utter_noworries
