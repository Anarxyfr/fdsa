import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1356810627909419079/5L26qDamgl753mBQL873Mq982SK6K4_2HH-mMmrfkOASId1GXyup-vVKOXbbDw6OC2iO"
LAST_MESSAGE_ID = None

def send_message(user, message):
    data = {
        "content": f"**{user}**: {message}"
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send message. Status code: {response.status_code}")

def get_messages():
    global LAST_MESSAGE_ID
    response = requests.get(WEBHOOK_URL + "?limit=1")
    
    if response.status_code == 200:
        messages = response.json()
        if messages and messages[0]['id'] != LAST_MESSAGE_ID:
            LAST_MESSAGE_ID = messages[0]['id']
            content = messages[0]['content']
            if not content.startswith("**User1**:"):  # Don't show your own messages
                print(f"\nReceived: {content}\nYou: ", end="")
    else:
        print(f"Failed to get messages. Status code: {response.status_code}")

def main():
    print("Simple P2P Chat using Discord Webhook")
    print("You are User1. Type 'exit' to quit.\n")
    
    while True:
        message = input("You: ")
        if message.lower() == 'exit':
            break
        
        send_message("User1", message)
        time.sleep(1)  # Wait a moment before checking for replies
        get_messages()

if __name__ == "__main__":
    main()
