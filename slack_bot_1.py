import sys
from slacker import Slacker

slack = Slacker('xoxb-1047057471891-1053942767041-JrP0D9ZXVDiYUAQc5LOAmfEy')

# Send a message to #general channel
message = 'Yo what\'s up everyone?'
slack.chat.post_message('#general', message)