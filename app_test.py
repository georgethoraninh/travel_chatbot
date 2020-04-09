import os
import ssl
import slack

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

client = slack.WebClient(token=slack_bot_token,
                         ssl=ssl_context)

response = client.chat_postMessage(
    channel='#general',
    text="Hey, I finally worked!")