import requests
import json
from datetime import date

# Function to get today's date in the format yyyy-mm-dd
def get_today_date():
    return date.today().strftime("%Y-%m-%d")

# Set your Trakt API credentials
access_token = "d267e1c912771bcc98565a8fc75bddadb63b5329d2990671819432bc4b87cad0"
client_id = "3000e66c77a21fc6dac2ef76d86fdb9ff4432ff39f5abcbf0b15e5413a34f3f0"

# Define URLs for movies and TV shows rated 9-10
movies_url = "https://api.trakt.tv/users/wdvhucb/ratings/movies/9-10"
shows_url = "https://api.trakt.tv/users/wdvhucb/ratings/shows/9-10"

# Set your list URL and remove URL
list_url = "https://api.trakt.tv/users/wdvhucb/lists/my-favourites/items"
remove_url = "https://api.trakt.tv/users/wdvhucb/lists/my-favourites/items/remove"

# Set your headers with authorization
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "trakt-api-version": "2",
    "trakt-api-key": client_id
}

try:
    # Send the GET request to fetch movies rated 9-10 from Trakt
    response_movies = requests.get(movies_url, headers=headers)

    # Send the GET request to fetch TV shows rated 9-10 from Trakt
    response_shows = requests.get(shows_url, headers=headers)

    # Check if both requests were successful (status code 200)
    if response_movies.status_code == 200 and response_shows.status_code == 200:
        # Parse the JSON responses to get movie and TV show data
        movie_data = response_movies.json()
        show_data = response_shows.json()

        # Extract movie and show IDs and titles
        movie_ids = [item['movie']['ids']['trakt'] for item in movie_data]
        show_ids = [item['show']['ids']['trakt'] for item in show_data]
        movie_titles = [item['movie']['title'] for item in movie_data]
        show_titles = [item['show']['title'] for item in show_data]

        # Debug: Print the movie and show IDs and titles
        print("Movies Retrieved:")
        for i in range(len(movie_ids)):
            print(f"Title: {movie_titles[i]}, ID: {movie_ids[i]}")

        print("\nShows Retrieved:")
        for i in range(len(show_ids)):
            print(f"Title: {show_titles[i]}, ID: {show_ids[i]}")

        # Create a list of movies and shows to add to the Trakt list
        items_to_add = {
            "movies": [{"ids": {"trakt": movie_id}} for movie_id in movie_ids],
            "shows": [{"ids": {"trakt": show_id}} for show_id in show_ids]
        }

        # Debug: Print the list of items to add
        print("\nItems to Add:")
        print("Movies:")
        for movie in items_to_add["movies"]:
            movie_title = next(iter(movie["ids"].values()))
            movie_id = movie["ids"]["trakt"]
            print(f"Title: {movie_title}, ID: {movie_id}")
        print("Shows:")
        for show in items_to_add["shows"]:
            show_title = next(iter(show["ids"].values()))
            show_id = show["ids"]["trakt"]
            print(f"Title: {show_title}, ID: {show_id}")

        # Fetch the current items in the Trakt list
        current_list_response = requests.get(list_url, headers=headers)

        # Check if the request for current list items was successful (status code 200)
        if current_list_response.status_code == 200:
            # Parse the JSON response to get the current list items
            current_list_items = current_list_response.json()

            # Extract movie and show titles from the current list
            current_movie_titles = [item['movie']['title'] for item in current_list_items if 'movie' in item]
            current_show_titles = [item['show']['title'] for item in current_list_items if 'show' in item]

            # Debug: Print the list of existing movie and show titles
            print("\nExisting Movies in the List:")
            for title in current_movie_titles:
                print(f"Title: {title}")
            print("\nExisting Shows in the List:")
            for title in current_show_titles:
                print(f"Title: {title}")

            # Determine movies and shows to remove
            movies_to_remove = [item for item in current_list_items if 'movie' in item and item['movie']['title'] not in movie_titles]
            shows_to_remove = [item for item in current_list_items if 'show' in item and item['show']['title'] not in show_titles]

            # Debug: Print the movies and shows to remove
            print("\nMovies to Remove:")
            for item in movies_to_remove:
                print(f"Title: {item['movie']['title']}, ID: {item['movie']['ids']['trakt']}")
            print("\nShows to Remove:")
            for item in shows_to_remove:
                print(f"Title: {item['show']['title']}, ID: {item['show']['ids']['trakt']}")

            # Create a JSON payload for removing items from the list
            remove_payload = {
                "movies": [{"ids": {"trakt": item['movie']['ids']['trakt']}} for item in movies_to_remove],
                "shows": [{"ids": {"trakt": item['show']['ids']['trakt']}} for item in shows_to_remove]
            }

            # Convert the payload to JSON
            remove_payload_json = json.dumps(remove_payload)

            # Send a POST request to remove items from the Trakt list
            remove_response = requests.post(remove_url, data=remove_payload_json, headers=headers)

            # Check if the remove request was successful (status code 200)
            if remove_response.status_code == 200:
                print("\nItems removed from the Trakt list successfully.")
            else:
                print(f"Error removing items from the Trakt list: {remove_response.status_code}")

            # Create a JSON payload for adding items to the list
            add_payload = items_to_add

            # Convert the payload to JSON
            add_payload_json = json.dumps(add_payload)

            # Send a POST request to add items to the Trakt list
            add_response = requests.post(list_url, data=add_payload_json, headers=headers)

            # Check if the add request was successful (status code 201)
            if add_response.status_code == 201:
                print("Items added to the Trakt list successfully.")
            else:
                print(f"Error adding items to the Trakt list: {add_response.status_code}")

        else:
            print(f"Error fetching current list items: {current_list_response.status_code}")

    else:
        print(f"Error fetching movies or TV shows: Movies({response_movies.status_code}), Shows({response_shows.status_code})")

except Exception as e:
    print(f"An error occurred: {str(e)}")
