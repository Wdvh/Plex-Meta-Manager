import requests
import json

# Trakt.tv API credentials
TRAKT_API_KEY = '0b07b6a8d02304e1bad2d7c90ce79d1c2157df25ffd893e093c89d84af1add75'
TRAKT_ACCESS_TOKEN = '307054604aa64f7e0faf779f3a38acadbaf82ba0c6d88829d966359fdbcff4cc'
TRAKT_USERNAME = 'wdvhucb'

# Discord webhook URL
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1143526278100701345/JAHdFwQCWWXrWZ-n3tCT4PXnSufITtvaaDJbPpc8FhJgZEfbZAFQT2wYs5xux7EJifHV'

# Define the genres and keywords to exclude
EXCLUDED_GENRES = ["anime", "biography", "children", "documentary", "fantasy", "holiday", "music", "musical", "romance", "sport", "tv movie", "film noir", "game show", "home and garden", "horror", "reality", "reality tv", "soap", "western"]
EXCLUDED_KEYWORDS = ["bollywood", "based on", "anime", "music", "musical", "biography"]

# Define the countries to exclude
EXCLUDED_COUNTRIES = ["china", "hong kong", "india", "south korea", "japan", "russia", "germany"]

def get_trakt_anticipated():
    url = f'https://api.trakt.tv/users/{TRAKT_USERNAME}/watchlist/anticipated'
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-key': TRAKT_API_KEY,
        'trakt-api-version': '2',
        'Authorization': f'Bearer {TRAKT_ACCESS_TOKEN}',
    }

    response = requests.get(url, headers=headers)
    return response.json()

def filter_and_update_trakt_list():
    anticipated_list = get_trakt_anticipated()
    movies_and_shows_to_add = []
    movies_and_shows_to_remove = []

    for item in anticipated_list:
        if 'movie' in item and (
            item['movie']['status'] in ['in_production', 'post_production'] and
            item['movie']['country'] not in EXCLUDED_COUNTRIES and
            not any(genre in item['movie']['genres'] for genre in EXCLUDED_GENRES) and
            not any(keyword in item['movie']['title'].lower() for keyword in EXCLUDED_KEYWORDS)
        ):
            movies_and_shows_to_add.append(item)
        elif 'show' in item and (
            item['show']['status'] in ['in_production', 'post_production'] and
            item['show']['country'] not in EXCLUDED_COUNTRIES and
            not any(genre in item['show']['genres'] for genre in EXCLUDED_GENRES) and
            not any(keyword in item['show']['title'].lower() for keyword in EXCLUDED_KEYWORDS)
        ):
            movies_and_shows_to_add.append(item)
        else:
            movies_and_shows_to_remove.append(item)
    # Remove items that don't meet the criteria
    for item in movies_and_shows_to_remove:
        url = f'https://api.trakt.tv/sync/watchlist/remove'
        data = {
            'movies': [{'ids': {'trakt': item['movie']['ids']['trakt']}}] if item['movie'] else [],
            'shows': [{'ids': {'trakt': item['show']['ids']['trakt']}}] if item['show'] else [],
        }
        requests.post(url, headers=headers, json=data)

    # Add items that meet the criteria
    for item in movies_and_shows_to_add:
        url = f'https://api.trakt.tv/sync/watchlist'
        data = {
            'movies': [{'ids': {'trakt': item['movie']['ids']['trakt']}}] if item['movie'] else [],
            'shows': [{'ids': {'trakt': item['show']['ids']['trakt']}}] if item['show'] else [],
        }
        requests.post(url, headers=headers, json=data)

    return movies_and_shows_to_add, movies_and_shows_to_remove

def send_discord_notification(added, removed):
    message = "Anticipated Movies and Shows Update:\n\n"
    
    if added:
        added_text = "\n".join([f"{item['movie']['title']} (Movie)" if item['movie'] else f"{item['show']['title']} (Show)" for item in added])
        message += f"**Added:**\n{added_text}\n\n"

    if removed:
        removed_text = "\n".join([f"{item['movie']['title']} (Movie)" if item['movie'] else f"{item['show']['title']} (Show)" for item in removed])
        message += f"**Removed:**\n{removed_text}"

    discord_data = {
        "content": message
    }

    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(discord_data), headers={'Content-Type': 'application/json'})
    if response.status_code != 204:
        print(f"Failed to send Discord message. Status code: {response.status_code}")

if __name__ == '__main__':
    added_items, removed_items = filter_and_update_trakt_list()
    send_discord_notification(added_items, removed_items)
