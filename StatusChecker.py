import requests
import time

USER_IDS = ["123456", "123456"] 
WEBHOOK_URL = "WEBHOOK_LOCATION" 
CHECK_INTERVAL = 10 

def get_usernames(user_ids):
    url = "https://users.roblox.com/v1/users"
    payload = {"userIds": user_ids}
    headers = {
        "Content-Type": "application/json"
    }

    print(f"[DEBUG] Sending request to {url} with payload {payload}")

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("[DEBUG] Successfully fetched usernames.")
        return {user["id"]: user["name"] for user in response.json().get("data", [])}
    else:
        print(f"[ERROR] Failed to fetch usernames. HTTP Status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text}")
        return {}

def get_user_status(user_ids):
    url = "https://presence.roblox.com/v1/presence/users"
    payload = {"userIds": user_ids}
    headers = {
        "Content-Type": "application/json"
    }

    print(f"[DEBUG] Sending request to {url} with payload {payload}")

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("[DEBUG] Successfully fetched user presence data.")
        return response.json().get("userPresences", [])
    else:
        print(f"[ERROR] Failed to fetch user presence. HTTP Status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text}")
        return []

def send_webhook_notification(user_data, usernames):
    status_message = {
        0: "Offline",
        1: "Online",
        2: "In Game",
        3: "In Studio"
    }

    for user in user_data:
        user_id = user.get("userId")
        username = usernames.get(user_id, "Unknown User")
        status = status_message.get(user.get("userPresenceType", 0), "Unknown")
        place_name = user.get("lastLocation", "N/A")

        content = f"**{username}** ({user_id}) is now **{status}**."
        if status == "In Game":
            content += f" Playing: {place_name}."

        print(f"[DEBUG] Preparing to send webhook notification: {content}")

        data = {
            "content": content
        }

        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"[DEBUG] Successfully sent notification for {username}.")
        else:
            print(f"[ERROR] Failed to send webhook for {username}. HTTP Status: {response.status_code}")
            print(f"[DEBUG] Webhook Response: {response.text}")

def monitor_users():
    last_statuses = {}
    print("[DEBUG] Starting user status monitoring...")
    while True:
        try:
            print("[DEBUG] Checking user statuses...")
            user_data = get_user_status(USER_IDS)
            usernames = get_usernames(USER_IDS)

            for user in user_data:
                user_id = user.get("userId")
                current_status = user.get("userPresenceType")

                if user_id not in last_statuses or last_statuses[user_id] != current_status:
                    print(f"[DEBUG] Status changed for {user_id}: {last_statuses.get(user_id)} -> {current_status}")
                    send_webhook_notification([user], usernames)
                    last_statuses[user_id] = current_status
                else:
                    print(f"[DEBUG] No status change detected for {user_id}.")

        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")

        print(f"[DEBUG] Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_users()
