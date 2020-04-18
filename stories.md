
## flight path
* request_flight
    - utter_ask_to_where
* inform{'place':'destination'}
    - utter_ask_from_where 
* inform{'place':'origin'}
    - utter_ask_duration
* inform{'date':'depart_date','date':'return_date'}
    - utter_budget
* inform{'budget':'$1000'}
    - utter_flight_offer
    - utter_ok
* affirm
    - goodbye

## flight path 1
* request_flight
* inform{'place':'origin'}
* inform{'place':'destination'}
* inform{'date':'depart_date','date':'return_date'}
* inform{'budget':'$1000'}
    - utter_flight_offer
    - utter_ok
* affirm
    - goodbye

## say hello
* greet
- utter_greeting

## say goodbye
* goodbye
  - utter_goodbye

## fallback
- utter_unclear

