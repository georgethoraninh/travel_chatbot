from rasa.core.channels.slack import SlackInput
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.model import get_model, get_model_subdirectories
from rasa.utils.endpoints import EndpointConfig
import os


slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

model_path = get_model("models/20200421-003512.tar.gz")

if not model_path:
    print("No model found.")
    exit(1)

_, nlu_model = get_model_subdirectories(model_path)
nlu_interpreter = RasaNLUInterpreter(nlu_model)

action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")

agent = Agent.load(
    model_path,
    interpreter = nlu_interpreter,
    action_endpoint = action_endpoint,
)

input_channel = SlackInput(slack_bot_token)
#agent.handle_channels([input_channel], 5005, serve_forever=True)
agent.handle_channels([input_channel], 5005)
