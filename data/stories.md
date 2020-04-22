
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

## interactive_story_2
* greet
    - utter_greet
* request_flight
    - flight_form
    - form{"name": "flight_form"}
    - slot{"requested_slot": "destination"}
* form: inform{"destination": "paris"}
    - form: flight_form
    - slot{"destination": "paris"}
    - slot{"requested_slot": "origin"}
* form: inform{"origin": "toronto"}
    - form: flight_form
    - slot{"origin": "toronto"}
    - slot{"requested_slot": "depart_date"}
* form: inform{"depart_date": "dec 12"}
    - form: flight_form
    - slot{"depart_date": "dec 12"}
    - slot{"requested_slot": "return_date"}
* form: inform{"return_date": "dec 22"}
    - form: flight_form
    - slot{"return_date": "dec 22"}
    - slot{"requested_slot": "budget"}
* form: inform{"budget": "$2000"}
    - form: flight_form
    - slot{"budget": "$2000"}
    - form{"name": null}
    - slot{"requested_slot": null}
* affirm
    - utter_ask_more_help
* deny
    - utter_noworries

## interactive_story_3
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
* form: inform{"budget": "$1000"}
    - form: flight_form
    - slot{"budget": "$1000"}
    - form{"name": null}
    - slot{"requested_slot": null}
* affirm
    - utter_ask_more_help
* deny
    - utter_noworries

## interactive_story_4
* greet
    - utter_greet
* request_flight
    - flight_form
    - form{"name": "flight_form"}
    - slot{"requested_slot": "destination"}
* form: inform{"destination": "vancouver"}
    - form: flight_form
    - slot{"destination": "vancouver"}
    - slot{"requested_slot": "origin"}
* form: inform{"origin": "toronto"}
    - form: flight_form
    - slot{"origin": "toronto"}
    - slot{"requested_slot": "depart_date"}
* form: inform{"depart_date": "sept 1"}
    - form: flight_form
    - slot{"depart_date": "sept 1"}
    - slot{"requested_slot": "return_date"}
* form: inform{"return_date": "sept 20"}
    - form: flight_form
    - slot{"return_date": "sept 20"}
    - slot{"requested_slot": "budget"}
* form: inform{"budget": "$500"}
    - form: flight_form
    - slot{"budget": "$500"}
    - form{"name": null}
    - slot{"requested_slot": null}
* affirm
    - utter_ask_more_help
* deny
    - utter_noworries
