
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
