import pandas as pd
import requests



api_key = 'xHyyMusZ2BWA54IgiP6z7g(('

# Specifying number of questions that needs to be fetched
num_questions = 10000 

#  URL for fetching questions
questions_url = f'https://api.stackexchange.com/2.3/questions?key={api_key}&site=stackoverflow&pagesize=100&page='

# function to fetch badges each user
def fetch_user_badges(user_id):
    badges_url = f'https://api.stackexchange.com/2.3/users/{user_id}/badges?key={api_key}&site=stackoverflow&pagesize=100'
    response = requests.get(badges_url)
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            badges = data['items']
            return badges
    return None

data_list = []

def fetching_data_stackoverflow(page: int):
    response = requests.get(questions_url + str(page))
    return response.json()

def api_to_csv_stackoverflow(no_of_pages_to_load):
    count = 0
    flag = 0
    for i in range(1, no_of_pages_to_load + 1):
        print(f"Requesting page {i}/{no_of_pages_to_load}")

        response = fetching_data_stackoverflow(i)

        if 'items' in response:
            result = response['items']

            for data in result:
                try:
                    str_tag = str(data.get('tags', ''))
                    tag_value = ((str_tag.replace("[", "").replace("]", "")).replace("'", ""))  # Tag Value
                    owner_reputation = data.get('owner', {}).get('reputation', 'NA')
                    owner_user_id = data.get('owner', {}).get('user_id', '')
                    owner_user_type = data.get('owner', {}).get('user_type', '')
                    owner_display_name = data.get('owner', {}).get('display_name', '')
                    is_answered = data.get('is_answered', False)
                    view_count = data.get('view_count', 0)
                    answer_count = data.get('answer_count', 0)
                    score = data.get('score', 0)
                    question_id = data.get('question_id', '')
                    title = data.get('title', '')


                    user_badges = fetch_user_badges(owner_user_id) # Fetch badges for the current user
                    if user_badges:
                        gold_badges = silver_badges = bronze_badges = 0
                        for badge in user_badges:
                            badge_type = badge['rank']
                            if badge_type == 'gold':
                                gold_badges += 1
                            elif badge_type == 'silver':
                                silver_badges += 1
                            elif badge_type == 'bronze':
                                bronze_badges += 1

                        data_list.append({
                            'Tag Value': tag_value,
                            'Owner Reputation': owner_reputation,
                            'Owner User ID': owner_user_id,
                            'Owner User Type': owner_user_type,
                            'Owner Display Name': owner_display_name,
                            'Is Answered': is_answered,
                            'View Count': view_count,
                            'Answer Count': answer_count,
                            'Score': score,
                            'Question ID': question_id,
                            'Title': title,
                            'Gold Badges': gold_badges,
                            'Silver Badges': silver_badges,
                            'Bronze Badges': bronze_badges,
                        })
                        flag += 1

                except:
                    count += 1
        else:
            print(f"No 'items' key in the response for page {i}")

    print("Invalid data:", count)
    print("Valid data:", flag)

    df = pd.DataFrame(data_list)

    df.to_csv('stackoverflow_with_badges.csv', index=False)
    print(f"Data saved to {'stackoverflow_with_badges.csv'}")

    #to save dataframe to the database with the table name "stack_data"
    #save_to_database(df, table_name="stack_data")

#main function calling
api_to_csv_stackoverflow(num_questions // 100)  # Dividing by 100 as each page fetches 100 questions