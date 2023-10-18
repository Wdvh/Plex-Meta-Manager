import requests
import json
from datetime import date, datetime
import pytz  # Import the pytz library for timezone conversion

# Function to get today's date in the format yyyy-mm-dd
def get_today_date():
    return date.today().strftime("%Y-%m-%d")

# Function to get today's date for the list descriptionin the format dd. mm. yyyy
def get_today_date_for_list():
    today = date.today()
    formatted_date = today.strftime("**%a** the **%d. %m. %Y**")
    return formatted_date

# Function to format a datetime string with timezone information
def format_datetime(datetime_str, timezone):
    if datetime_str:
        # Parse the datetime string and convert it to a datetime object
        dt = datetime.fromisoformat(datetime_str)

        # Convert to the specified timezone
        dt = dt.astimezone(pytz.timezone(timezone))

        # Format the datetime in the desired format
        formatted_datetime = dt.strftime("\nat **%H:%M** on **%a** the **%d. %m. %Y**")

        return formatted_datetime
    return ""

# Set your API endpoint URL with the dynamic date
url = f"https://api.trakt.tv/calendars/my/shows/premieres/{get_today_date()}/92"

# Set the Trakt list URL and remove URL
list_url = "https://api.trakt.tv/users/wdvhucb/lists/returning/items"
remove_url = "https://api.trakt.tv/users/wdvhucb/lists/returning/items/remove"

# Set your Trakt API credentials
access_token = "18c56d225150306f61ce100a9d3135443c7539f5d572e0002575da5e5ade0787"
client_id = "0b07b6a8d02304e1bad2d7c90ce79d1c2157df25ffd893e093c89d84af1add75"

# Set your webhook URL
webhook_url = "https://discord.com/api/webhooks/1143526278100701345/JAHdFwQCWWXrWZ-n3tCT4PXnSufITtvaaDJbPpc8FhJgZEfbZAFQT2wYs5xux7EJifHV"  # Replace with your actual webhook URL

# Set your headers with authorization
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "trakt-api-version": "2",
    "trakt-api-key": client_id
}

def update_list_description(new_description):
    # Set the correct Trakt list URL for updating the list description
    update_list_url = "https://api.trakt.tv/users/wdvhucb/lists/returning"
    update_payload = {
        "description": new_description
    }
    # Send a JSON PUT request to update the list description
    update_response = requests.put(update_list_url, data=json.dumps(update_payload), headers=headers)
    
    # Print Trakt API response code for debugging
    print(f"Update Response Code: {update_response.status_code}")

try:
    # Send the GET request to fetch TV shows from the Trakt API
    response = requests.get(url, headers=headers)

    # Initialize notification_text
    notification_text = ""

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response to get TV show data
        tv_show_data = response.json()

        # Sort the TV shows by their premiere date and time
        sorted_tv_show_data = sorted(tv_show_data, key=lambda x: x['first_aired'])

        # Extract the TV show titles and store them in a list
        tv_show_titles = [show['show']['title'] for show in sorted_tv_show_data]

        # Fetch the list items (shows) from the Trakt list
        list_response = requests.get(list_url, headers=headers)

        # Check if the request was successful (status code 200)
        if list_response.status_code == 200:
            # Parse the JSON response to get the list items (shows)
            list_items = list_response.json()

            # Create a set of existing show titles for faster lookup
            existing_show_titles = {item['show']['title'] for item in list_items}

            # Create a list of shows to add to the Trakt list (only missing shows)
            shows_to_add = []
            for show in sorted_tv_show_data:
                show_title = show['show']['title']
                if show_title not in existing_show_titles:
                    shows_to_add.append({"ids": {"trakt": show['show']['ids']['trakt']}, "title": show_title, "first_aired": show.get('first_aired', '')})

            # Determine the shows to remove (those not in tv_show_titles)
            shows_to_remove = []
            for item in list_items:
                item_title = item['show']['title']
                if item_title not in tv_show_titles:
                    shows_to_remove.append({"ids": {"trakt": item['show']['ids']['trakt']}, "title": item_title, "first_aired": item.get('first_aired', '')})

            # Create a JSON payload for removing items from the list
            remove_payload = {
                "shows": [{"ids": {"trakt": item['ids']['trakt']}} for item in shows_to_remove]
            }

            # Send a POST request to remove shows from the Trakt list
            remove_response = requests.post(remove_url, data=json.dumps(remove_payload), headers=headers)

            # Print Trakt API response code for debugging
            print(f"Remove Response Code: {remove_response.status_code}")

            # Create a JSON payload for adding items to the list
            add_payload = {
                "shows": [{"ids": {"trakt": show['ids']['trakt']}} for show in shows_to_add]
            }

            # Send a POST request to add shows to the Trakt list
            add_response = requests.post(list_url, data=json.dumps(add_payload), headers=headers)

            # Print Trakt API response code for debugging
            print(f"Add Response Code: {add_response.status_code}")

            # Determine if items were added or removed
            items_changed = shows_to_add or shows_to_remove

            # Get today's date
            last_changed_text = get_today_date_for_list()

            if items_changed:
                # Include the list description with the last changed date
                list_description = f"TV shows that air a new season in the next 3 months.\nThis list was last changed on {last_changed_text}."

                # Update the list description with the last changed date
                update_list_description(list_description)

                # Build the notification text
                notification_text += "\n**Changed the Trakt List Returning**\n"

                if shows_to_add:
                    notification_text += "\n**added TV Shows:**\n"
                    notification_text += f"API Response Code: **{add_response.status_code}**\n\n"
                    for show in shows_to_add:
                        trakt_url = f"<https://trakt.tv/shows/{show['ids']['trakt']}>"
                        formatted_datetime = format_datetime(show['first_aired'], "Europe/Berlin")
                        notification_text += f"**[{show['title']}]({trakt_url})** {formatted_datetime}\n"
                    
                if shows_to_remove:
                    notification_text += "\n**removed TV Shows:**\n"
                    notification_text += f"API Response Code: **{remove_response.status_code}**\n\n"
                for item in shows_to_remove:
                    trakt_url = f"[**{item['title']}**](<https://trakt.tv/shows/{item['ids']['trakt']}>)"
                    notification_text += f"{trakt_url}\n"

        # Send the notification to the webhook
        response = requests.post(webhook_url, json={"content": notification_text})

    else:
        print(f"Error fetching TV shows: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
