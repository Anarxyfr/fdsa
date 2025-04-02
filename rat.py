import requests
import time

# === Setup ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1356810627909419079/5L26qDamgl753mBQL873Mq982SK6K4_2HH-mMmrfkOASId1GXyup-vVKOXbbDw6OC2iO"  # Your Discord Webhook URL

# === Chat Reply Logic ===
def send_reply(message):
    """Send the reply back to the Discord Webhook."""
    data = {"content": message}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"Sent reply: {message}")
    else:
        print(f"Failed to send reply: {response.status_code}")

# === Webhook Command Polling ===
def check_for_messages():
    """Check the Discord Webhook for incoming messages."""
    while True:
        try:
            # Poll the webhook for new messages (commands)
            response = requests.get(WEBHOOK_URL)
            if response.status_code == 200:
                data = response.json()
                if 'content' in data:  # Look for the 'content' of the message
                    message = data['content'].strip()
                    if message:
                        print(f"Received message: {message}")
                        reply = f"Your message '{message}' has been received!"
                        send_reply(reply)  # Send back a reply

        except Exception as e:
            print(f"[!] Error checking for messages: {e}")
        
        time.sleep(5)  # Wait 5 seconds before checking again

# === Main Execution ===
if __name__ == "__main__":
    check_for_messages()
