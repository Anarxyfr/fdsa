import discord
import requests
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1356810627909419079/5L26qDamgl753mBQL873Mq982SK6K4_2HH-mMmrfkOASId1GXyup-vVKOXbbDw6OC2iO"
BOT_TOKEN = "MTM1NjgwNzIyMTgxOTk5ODIzOQ.GugL7a.B6pyc-ehNYTI7crXr8V433riRTvLd7tNg8AQtg"  # Replace with your bot token
PEER_NAME = "Peer1"
OTHER_PEER = "Peer2"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class ChatClient(discord.Client):
    async def on_ready(self):
        print(f"{PEER_NAME} ready! Type messages below:")

    async def on_message(self, message):
        if message.author == self.user or not message.webhook_id:
            return
        
        content = message.content
        if content.startswith(f"[{OTHER_PEER}]"):
            print(f"\n{OTHER_PEER}: {content[len(OTHER_PEER)+2:]}\n> ", end='')

def send_messages():
    while True:
        message = input("> ")
        requests.post(WEBHOOK_URL, json={"content": f"[{PEER_NAME}] {message}"})

def run_bot():
    client = ChatClient(intents=intents)
    client.run(BOT_TOKEN)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    send_messages()
