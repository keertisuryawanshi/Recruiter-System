import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import numpy as np
import sys
sys.path.append('C:\\Users\\Keertisuryawanshi\\Desktop\\Python_Group 9\\database')
from connection import save_to_database, engine

def get_top_candidates(job_role):
    # Function to count exact skill matches in the 'Tag Value' column
    def count_exact_skill_matches(tag_value, skill_list):
        if pd.isna(tag_value):
            return 0
        tags = set(tag_value.lower().replace(",", " ").split())
        return sum(skill.lower() in tags for skill in skill_list)

    # Load the job roles data and stackoverflow data
    job_roles_query = "SELECT * FROM job_roles"
    stackoverflow_query = "SELECT * FROM unseen_data"
    job_roles_df = pd.read_sql(job_roles_query, engine)
    stackoverflow_df = pd.read_sql(stackoverflow_query, engine)

    # Extract skills list and add skill count columns to the Stack Overflow dataset for each job role
    job_roles_df['Skills List'] = job_roles_df['Skills'].apply(lambda x: [skill.strip().lower() for skill in x.split(',')])
    for role in job_roles_df['Job Roles']:
        stackoverflow_df[role + ' Count'] = stackoverflow_df['Tag Value'].apply(lambda x: count_exact_skill_matches(x, job_roles_df.loc[job_roles_df['Job Roles'] == role, 'Skills List'].values[0]))

    # Normalize the features for KMeans
    feature_cols = ['Owner Reputation', 'Gold Badges', 'Silver Badges', 'Bronze Badges'] + [role + ' Count' for role in job_roles_df['Job Roles']]
    features = stackoverflow_df[feature_cols]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Load the pre-trained KMeans model from the pickle file
    with open('C:\\Users\\Keertisuryawanshi\\Desktop\\Python_Group 9\\evaluation_system\\kmeans_model.pkl', 'rb') as file:  # Update this path
        loaded_kmeans = pickle.load(file)

    # Use the loaded model to predict clusters on the stackoverflow data
    stackoverflow_df['Predicted Cluster'] = loaded_kmeans.predict(features_scaled)

    # Analyze the centroids of the clusters from the loaded model
    centroids = pd.DataFrame(scaler.inverse_transform(loaded_kmeans.cluster_centers_), columns=feature_cols)

    # Plotting a heatmap for the cluster centroids
    # plt.figure(figsize=(14, 10))
    # sns.heatmap(centroids, annot=True, fmt=".2f", cmap="YlGnBu")
    # plt.title('Heatmap of Cluster Centroids')
    # plt.show()

    # Determine the most representative job role for each cluster based on the centroids
    def get_dominant_role_for_cluster(centroid, job_roles):
        return job_roles[np.argmax(centroid[-len(job_roles):])]

    dominant_roles = {}
    for i, row in centroids.iterrows():
        dominant_roles[i] = get_dominant_role_for_cluster(row.values, job_roles_df['Job Roles'])

    # Extract top candidates from each cluster for the corresponding job role
    top_candidates_per_role = {}
    for cluster, job_role in dominant_roles.items():
        role_count_column = job_role + ' Count'
        cluster_df = stackoverflow_df[stackoverflow_df['Predicted Cluster'] == cluster]
        top_candidates = cluster_df.sort_values(by=[role_count_column, 'Owner Reputation', 'Gold Badges', 'Silver Badges', 'Bronze Badges'], ascending=False).head(10)
        
        #Adding email addresses for every candidate
        top_candidates['owner_email_address'] = np.repeat(['dataengine73@gmail.com', 'user04@example.com'], len(top_candidates) // 2)
        
        #Creating Email address according to display name
        #top_candidates['Owner Email Address'] = top_candidates['Owner Display Name'].apply(lambda x: f"{x.replace(' ', '_').lower()}@gmail.com")

        top_candidates_per_role[job_role] = top_candidates

    # # Optionally, save or print top candidates for each job role
    # for role, candidates in top_candidates_per_role.items():
    #     print(f"Top candidates for {role}:")
    #     print(candidates[['Owner Display Name', 'Owner Reputation', 'Gold Badges', 'Silver Badges', 'Bronze Badges', role + ' Count']], "\n")
    #     candidates.to_csv(f'{role}122.csv', index=False)

    # Save top candidates to the database
    for role, candidates_df in top_candidates_per_role.items():
        # convert the role name to lowercase and replace spaces with underscores
        role_lower_with_underscore = role.lower().replace(' ', '_')
        table_name = f'candidates_{role_lower_with_underscore}'
        save_to_database(candidates_df, table_name)
