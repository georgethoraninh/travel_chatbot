
## flight path
* request_flight
    - utter_ask_to_where
* inform{'destination':'tokyo'}
    - utter_ask_from_where 
* inform{'place':'toronto'}
    - utter_ask_duration
* inform{'depart_date':'2020-10-01T00:00:00','return_date':'2020-10-15T00:00:00'}
    - utter_budget
* inform{'budget':'1000'}
    - action_flight_offer
    - utter_ok
* affirm
    - utter_goodbye

## flight path 1
* request_flight
* inform{'place':'origin'}
* inform{'place':'destination'}
* inform{'date':'depart_date','date':'return_date'}
* inform{'budget':'1000'}
    - action_flight_offer
    - utter_ok
* affirm
    - utter_goodbye

## say hello
* greet
    - utter_greeting

## say goodbye
* goodbye
    - utter_goodbye

## fallback
    - utter_unclear

