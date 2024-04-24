import requests
import csv
import threading
from queue import Queue
import time

# Constants
ACCESS_TOKEN = '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'  # Use your actual GitHub access token
API_URL_BASE = 'https://api.github.com/search/users'
PER_PAGE = 100  # Max value allowed by GitHub API for per_page parameter
TOTAL_USERS = 5000  # Total number of users you want to fetch
CONCURRENT_REQUESTS = 10  # Adjust based on your rate limit and system capabilities
WAIT_SECONDS = 10  # Time to wait before issuing new batches of requests

# Headers for authentication
headers = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

# Queue for threads
user_queue = Queue()

# Lock for writing to the CSV file
csv_lock = threading.Lock()

# Function definitions (fetch_user_details, save_to_csv, execute_threads) remain unchanged
def fetch_user_details():
    while not user_queue.empty():
        username = user_queue.get()
        try:
            user_details_url = f"https://api.github.com/users/{username}"
            repos_url = f"{user_details_url}/repos"

            user_response = requests.get(user_details_url, headers=headers)
            user_response.raise_for_status()  # Raises stored HTTPError, if one occurred

            repos_response = requests.get(repos_url, headers=headers)
            repos_response.raise_for_status()

            user_data = user_response.json()
            repos_data = repos_response.json()

            languages = {}
            #starred_counts = []  # List to hold star counts for each repository

            for repo in repos_data:
                language = repo.get('language')
                if language:
                    languages[language] = languages.get(language, 0) + 1
                # Append repository name and its star count to the list
                #starred_counts.append(f"{repo['name']}: {repo['stargazers_count']} stars")

            languages_str = "; ".join([f"{lang}: {count}" for lang, count in languages.items()])
            #starred_counts_str = "; ".join(starred_counts)  # Convert list to a string for CSV output

            user_details = {
                'git_user_name': user_data.get('name'),
                'git_login_name': user_data.get('login'),
                'git_followers': user_data.get('followers'),
                'git_created_at': user_data.get('created_at'),
                'git_total_starred_count': sum([repo['stargazers_count'] for repo in repos_data]),  # Sum of all stars across repositories
                'git_repo_count': len(repos_data),
                'git_repository': repos_data[0]['full_name'] if repos_data else 'None',
                'git_user_email': user_data.get('email'),
                'languages_usage': languages_str,
                #'starred_counts': starred_counts_str
            }

            with csv_lock:
                save_to_csv([user_details])

        except requests.exceptions.RequestException as e:
            print(f"Request error for user {username}: {e}")

        except Exception as e:
            print(f"Unexpected error for user {username}: {e}")

        finally:
            user_queue.task_done()

def save_to_csv(users_data, mode='a'):
    csv_file = 'github_users_data_final_1.csv'
    csv_columns = ['git_user_name', 'git_login_name', 'git_followers', 'git_created_at', 
                   'git_total_starred_count', 'git_repo_count', 
                   'git_repository', 'git_user_email', 'languages_usage']
    
    with open(csv_file, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        if mode == 'w':
            writer.writeheader()
        writer.writerows(users_data)

def main():
    save_to_csv([], mode='w')  # Initialize CSV file with headers

    users_fetched = 0
    page = 1

    while users_fetched < TOTAL_USERS:
        search_params = {
            'q': 'type:user',  # Search for user accounts
            'sort': 'followers',  # Optional: Sort users by number of followers
            'per_page': PER_PAGE,
            'page': page,
        }
        response = requests.get(API_URL_BASE, headers=headers, params=search_params)
        if response.status_code != 200:
            print(f"Error fetching users: {response.status_code}")
            print(response.text)
            break

        data = response.json().get('items', [])
        if not data:
            break  #no more users to fetch

        for user in data:
            user_queue.put(user['login'])
            users_fetched += 1
            if users_fetched >= TOTAL_USERS:
                break

        execute_threads()

        page += 1
        if users_fetched >= TOTAL_USERS:
            break

        time.sleep(WAIT_SECONDS)

def execute_threads():
    threads = []
    for _ in range(min(CONCURRENT_REQUESTS, user_queue.qsize())):
        thread = threading.Thread(target=fetch_user_details)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()