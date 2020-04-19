import logging
import asyncio
import rasa.core
from rasa.core.agent import Agent
from rasa.core.policies.fallback import FallbackPolicy
from rasa.core.policies.keras_policy import KerasPolicy
from rasa.core.policies.memoization import MemoizationPolicy
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.run import serve_application
from rasa.core import config
from rasa.core.actions import Action

logger = logging.getLogger(__name__)

class ApiAction(Action):
	def name(self):
		return "action_flight_offer"
	
	def submit(self, dispatcher,tracker,domain):
		destination = tracker.get_slot('destination')
		origin = tracker.get_slot('origin')
		depart_date = tracker.get_slot('depart_date')
		return_date = tracker.get_slot('return_date')
		budget = tracker.get_slot('budget')
		
		dispatcher.utter_message(f'Testing:{destination},{origin},{depart_date},{return_date},{budget}')

def train_dialogue(domain_file='domain.yml',
				   model_path='models/dialogue',
				   training_data_file='stories.md'):
	
	# fallback = FallbackPolicy(fallback_action_name="utter_unclear",
	# 					  core_threshold=0.2,
	# 					  nlu_threshold=0.1)
	
	agent = Agent(domain_file, policies=[MemoizationPolicy(),
										 KerasPolicy(epochs=200)])
										 #fallback])

	#loop = asyncio.get_event_loop()
	#data = loop.run_until_complete(agent.load_data(training_data_file))
	#training_data = asyncio.run(agent.load_data(training_data_file))
	#training_data = await agent.load_data(training_data_file)
	training_data = asyncio.run(agent.load_data(training_data_file))
	agent.train(training_data)
	#agent.train(data)

	agent.persist(model_path)
	return agent

def run_travel_bot(serve_forever=True):
	interpreter = RasaNLUInterpreter('./models/nlu/current')
	agent = Agent.load('./models/dialogue', interpreter=interpreter)
	#rasa.core.run.serve_application(agent, channel='cmdline')
	print("Your bot is ready to talk! Type your messages here or send 'stop'")
	while True:
	    a = input()
	    if a == 'stop':
	        break
	    responses = asyncio.run(agent.handle_message(a))
	    for response in responses:
	        print(response["text"])

	return agent

if __name__ == '__main__':
	#train_dialogue()
	# interpreter = RasaNLUInterpreter('./models/nlu/current')
	# agent = Agent.load('./models/dialogue', interpreter=interpreter)
	# print("Your bot is ready to talk! Type your messages here or send 'stop'")
	# while True:
	#     a = input()
	#     if a == 'stop':
	#         break
	#     responses = asyncio.run(agent.handle_message(a))
	#     for response in responses:
	#         print(response["text"])
	run_travel_bot()