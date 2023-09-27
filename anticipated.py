
import requests
import json
from datetime import datetime, timedelta

def calculate_years():
    # Get the current date
    current_date = datetime.now()

    # Calculate year1 as today minus 60 days
    year1_date = current_date - timedelta(days=60)
    year1 = year1_date.year

    # Calculate year2 as 10 years from today
    year2 = current_date.year + 5

    return year1, year2

# Call the calculate_years function to get year1 and year2
year1, year2 = calculate_years()

# You can now use year1 and year2 to construct the URL elsewhere in your script
print(f"year1: {year1}")
print(f"year2: {year2}")

# Set your Trakt API credentials
access_token = "307054604aa64f7e0faf779f3a38acadbaf82ba0c6d88829d966359fdbcff4cc"
client_id = "0b07b6a8d02304e1bad2d7c90ce79d1c2157df25ffd893e093c89d84af1add75"
username = "wdvhucb"  # Replace with your Trakt username

# Set your headers with authorization
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "trakt-api-version": "2",
    "trakt-api-key": client_id
}

# Function to fetch and merge the lists with extended info
def fetch_and_merge_lists(url, list_name):
    print(f"Fetching and sorting {list_name} from URL: {url}...")  # Print the URL being fetched
    response = requests.get(url, headers=headers)
    print(f"Status Code for {list_name}: {response.status_code}")  # Print the status code
    if response.status_code == 200:
        data = response.json()
        print(f"Fetched {len(data)} items from {list_name} (Status Code {response.status_code}).")
        return data
    else:
        print(f"Failed to fetch data from {list_name} (Status Code {response.status_code}).")
        return []

# Function to fetch anticipated items from a given URL
def fetch_anticipated_items(url, item_type):
    print(f"Fetching anticipated {item_type} from URL: {url}...")  # Print the URL being fetched
    items = []
    page = 1
    while page <= 10:  # Loop through the first 50 pages
        response = requests.get(f"{url}&page={page}", headers=headers)
        print(f"Status Code for anticipated {item_type} (Page {page}): {response.status_code}")  # Print the status code
        if response.status_code == 200:
            page_items = response.json()
            if not page_items:
                break
            items.extend(page_items)
            page += 1
        else:
            print(f"Failed to fetch data from {item_type} (Status Code {response.status_code}).")
            break
    print(f"Fetched {len(items)} anticipated {item_type} (Status Code {response.status_code}).")
    return items

# Define the URLs for watchlist, list items, and anticipated items
watchlist_url = f"https://api.trakt.tv/users/{username}/watchlist/movies,shows"
collection_movies_url = f"https://api.trakt.tv/users/{username}/collection/movies"
collection_shows_url = f"https://api.trakt.tv/users/{username}/collection/shows"
list_url = "https://api.trakt.tv/users/wdvhucb/lists/sounds-interesting/items/movies,shows"
blocked_url = "https://api.trakt.tv/users/wdvhucb/lists/blocked/items/movies,shows"
anticipated_movies_url = f"https://api.trakt.tv/movies/anticipated?extended=full&years={year1}-{year2}&language=en,de,es&countries=au,ca,co,de,mx,nz,gb,us&genre=-anime,-documentary,-donghua,-fantasy,-music,-musical,-none,-romance,-sporting-event,-western"
anticipated_shows_url = f"https://api.trakt.tv/shows/anticipated?extended=full&years={year1}-{year2}&language=en,de,es&countries=au,ca,co,de,mx,nz,gb,us&status=in+production,pilot,returning+series,upcoming&genres=-anime,-children,-documentary,-donghua,-fantasy,-game-show,-home-and-garden,-music,-news,-none,-reality,-romance,-soap,-special-interest,-sporting-event,-talk-show,-western"

# Fetch and merge watchlist and list items
watchlist_data = fetch_and_merge_lists(watchlist_url, "watchlist")
collection_movies_data = fetch_and_merge_lists(collection_movies_url, "collection_movies")
collection_shows_data = fetch_and_merge_lists(collection_shows_url, "collection_shows")
list_data = fetch_and_merge_lists(list_url, "List 'sounds-interesting'")
blocked_data = fetch_and_merge_lists(blocked_url, "List 'blocked'")

# Combine the three lists
combined_list = watchlist_data + list_data + blocked_data + collection_movies_data + collection_shows_data

# Print the combined list
print("\nCombined List:")
for item in combined_list:
    if 'movie' in item:
        print(f"{item['movie']['title']} - Type: Movie")
    elif 'show' in item:
        print(f"{item['show']['title']} - Type: Show")

# Separate movies and shows
movies = [item['movie']['ids']['trakt'] for item in combined_list if 'type' in item and item['type'] == 'movie' and 'movie' in item]
shows = [item['show']['ids']['trakt'] for item in combined_list if 'type' in item and item['type'] == 'show' and 'show' in item]

# Fetch anticipated movies and shows
anticipated_movies = fetch_anticipated_items(anticipated_movies_url, "Movies")
anticipated_shows = fetch_anticipated_items(anticipated_shows_url, "Shows")

# Define the genres to exclude
excluded_genres = ["anime", "documentary", "donghua", "fantasy", "music", "musical", "romance", "sporting event", "western", "children", "game show", "home and garden", "news", "reality", "soap", "special interest", "sporting event", "talk show"]

# Define the languages to include
included_languages = ["de", "en", "es"]

# Function to filter out items already in the watchlist or sounds-interesting list,
# exclude specified genres, and ensure specified languages
def filter_items_not_in_lists_and_exclude_genres_and_languages(anticipated_items, existing_items, excluded_genres, included_languages):
    filtered_items = []
    for item in anticipated_items:
        if ('movie' in item and item['movie']['ids']['trakt'] not in existing_items) or \
           ('show' in item and item['show']['ids']['trakt'] not in existing_items):
            if ('movie' in item and 'genres' in item['movie'] and not any(genre in item['movie']['genres'] for genre in excluded_genres)) or \
               ('show' in item and 'genres' in item['show'] and not any(genre in item['show']['genres'] for genre in excluded_genres)):
                if ('movie' in item and 'language' in item['movie'] and item['movie']['language'] in included_languages) or \
                   ('show' in item and 'language' in item['show'] and item['show']['language'] in included_languages):
                    filtered_items.append(item)
    return filtered_items

# Filter out anticipated movies and shows that are already in watchlist or sounds-interesting,
# exclude specified genres, and ensure specified languages
filtered_movies = filter_items_not_in_lists_and_exclude_genres_and_languages(anticipated_movies, movies, excluded_genres, included_languages)
filtered_shows = filter_items_not_in_lists_and_exclude_genres_and_languages(anticipated_shows, shows, excluded_genres, included_languages)

# Print or process the filtered lists as needed
print("\nAnticipated Movies:")
for movie in filtered_movies:
    if 'movie' in movie:
        print(f"{movie['movie']['title']} - Genres: {', '.join(movie['movie']['genres'])}, Language: {movie['movie']['language']}")

print("\nAnticipated Shows:")
for show in filtered_shows:
    if 'show' in show:
        print(f"{show['show']['title']} - Genres: {', '.join(show['show']['genres'])}, Language: {show['show']['language']}")
# Define the Trakt list URL
trakt_list_url = "https://api.trakt.tv/users/wdvhucb/lists/anticipated/items"

# Combine filtered movies and shows into a single list
filtered_items = filtered_movies + filtered_shows

# Create a list of Trakt IDs for the filtered items
trakt_ids = [item['movie']['ids']['trakt'] if 'movie' in item else item['show']['ids']['trakt'] for item in filtered_items]

# Prepare the data to be added to the Trakt list
data = {
    "movies": [{"ids": {"trakt": trakt_id}} for trakt_id in trakt_ids],
    "shows": [{"ids": {"trakt": trakt_id}} for trakt_id in trakt_ids]
}

# Convert the data to JSON format
data_json = json.dumps(data)

# Set up headers for the request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "trakt-api-version": "2",
    "trakt-api-key": client_id
}

# Fetch the current items in the 'anticipated' list on Trakt
list_items_url = "https://api.trakt.tv/users/wdvhucb/lists/anticipated/items"
# ...

# Fetch the current items in the 'anticipated' list on Trakt
response = requests.get(list_items_url, headers=headers)

# Check the response status
if response.status_code == 200:
    current_items = response.json()
else:
    print(f"Failed to fetch current items from the Trakt list. Status Code: {response.status_code}")
    current_items = []

# Extract Trakt IDs of the current items in the list
current_trakt_ids = [item['movie']['ids']['trakt'] if 'movie' in item else item['show']['ids']['trakt'] for item in current_items]

# Identify items to add and remove
items_to_add = [item for item in filtered_items if ('movie' in item and item['movie']['ids']['trakt'] not in current_trakt_ids) or
                                               ('show' in item and item['show']['ids']['trakt'] not in current_trakt_ids)]
items_to_remove = [item for item in current_items if ('movie' in item and item['movie']['ids']['trakt'] not in trakt_ids) or
                                               ('show' in item and item['show']['ids']['trakt'] not in trakt_ids)]

# Print items added to the anticipated list
print("\nItems Added to 'anticipated' List:")
for item in items_to_add:
    if 'movie' in item:
        print(f"{item['movie']['title']} - Type: Movie")
        print("Reason: New item or not in 'anticipated' list")
    elif 'show' in item:
        print(f"{item['show']['title']} - Type: Show")
        print("Reason: New item or not in 'anticipated' list")

# Print items removed from the anticipated list
print("\nItems Removed from 'anticipated' List:")
for item in items_to_remove:
    if 'movie' in item:
        print(f"{item['movie']['title']} - Type: Movie")
        print("Reason: No longer in the filtered list or no longer meets criteria")
    elif 'show' in item:
        print(f"{item['show']['title']} - Type: Show")
        print("Reason: No longer in the filtered list or no longer meets criteria")

# Add new items to the Trakt list
if items_to_add:
    add_data = {
        "movies": [{"ids": {"trakt": trakt_id}} for trakt_id in trakt_ids],
        "shows": [{"ids": {"trakt": trakt_id}} for trakt_id in trakt_ids]
    }
    add_data_json = json.dumps(add_data)
    add_response = requests.post(list_items_url, headers=headers, data=add_data_json)

    if add_response.status_code == 200:
        print("\nNew items added to the Trakt list 'anticipated'.")
    else:
        print(f"Failed to add new items to the Trakt list. Status Code: {add_response.status_code}")

# Remove items that no longer belong to the Trakt list
if items_to_remove:
    for item in items_to_remove:
        item_id = item['movie']['ids']['trakt'] if 'movie' in item else item['show']['ids']['trakt']
        item_type = 'movies' if 'movie' in item else 'shows'
        remove_url = f"https://api.trakt.tv/users/wdvhucb/lists/anticipated/items/remove"
        
        # Prepare the data to be removed from the Trakt list
        remove_data = {
            item_type: [{"ids": {"trakt": item_id}}]
        }
        
        remove_data_json = json.dumps(remove_data)
        remove_response = requests.post(remove_url, headers=headers, data=remove_data_json)

        if remove_response.status_code == 200:
            print(f"Item {item_id} removed from the Trakt list 'anticipated'.")
        else:
            print(f"Failed to remove item {item_id} from the Trakt list. Status Code: {remove_response.status_code}")

# Send a POST request to add items to the Trakt list
response = requests.post(trakt_list_url, headers=headers, data=data_json)

# Check the response status
if response.status_code == 201:
    print("\nItems successfully added to the Trakt list 'anticipated'.")
else:
    print(f"Failed to add items to the Trakt list. Status Code: {response.status_code}")
