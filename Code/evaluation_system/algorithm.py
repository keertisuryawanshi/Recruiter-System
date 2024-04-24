import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import sys
sys.path.append('C:\\Users\\Keertisuryawanshi\\Desktop\\Python\\database')
from connection import save_to_database

def process_and_save_candidates__(job_role):
# Load datasets

    job_roles_df = pd.read_excel('C:/Users/Keertisuryawanshi/Desktop/Python/evaluation_system/Job_roles.xlsx')
    stackoverflow_df = pd.read_csv('C:/Users/Keertisuryawanshi/Desktop/Python/evaluation_system/stackoverflow_with_badges.csv')

    # Define a function to count exact skill matches in the 'Tag Value' column
    def count_exact_skill_matches(tag_value, skill_list):
        if pd.isna(tag_value):
            return 0
        tags = set(tag_value.lower().replace(",", " ").split())
        return sum(skill.lower() in tags for skill in skill_list)

    # Extract skills list and add skill count columns to the Stack Overflow dataset for each job role
    job_roles_df['Skills List'] = job_roles_df['Skills'].apply(lambda x: [skill.strip().lower() for skill in x.split(',')])
    for role in job_roles_df['Job Roles']:
        stackoverflow_df[role + ' Count'] = stackoverflow_df['Tag Value'].apply(lambda x: count_exact_skill_matches(x, job_roles_df.loc[job_roles_df['Job Roles'] == role, 'Skills List'].values[0]))

    # Normalize the features for KMeans
    feature_cols = ['Owner Reputation', 'Gold Badges', 'Silver Badges', 'Bronze Badges'] + [role + ' Count' for role in job_roles_df['Job Roles']]
    features = stackoverflow_df[feature_cols]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Use the Elbow method to find the optimal number of clusters
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(features_scaled)
        wcss.append(kmeans.inertia_)

    # Plot the Elbow graph
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 11), wcss)
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.show()


    # Determine the optimal number of clusters and fit KMeans
    optimal_clusters = 6  # Replace with the chosen number based on the Elbow graph
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    kmeans.fit(features_scaled)

    # Assign cluster labels to the original dataframe
    stackoverflow_df['Cluster'] = kmeans.labels_

    # Analyze the centroids
    centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=feature_cols)

    # Plotting a heatmap for the cluster centroids
    plt.figure(figsize=(14, 10))
    sns.heatmap(centroids, annot=True, fmt=".2f", cmap="YlGnBu")
    plt.title('Heatmap of Cluster Centroids')
    plt.show()

    # Determine the most representative job role for each cluster based on the centroids
    def get_dominant_role_for_cluster(centroid, job_roles):
        return job_roles[np.argmax(centroid[-len(job_roles):])]

    # Create a dictionary to hold the dominant job role for each cluster
    dominant_roles = {}
    for i, row in centroids.iterrows():
        dominant_roles[i] = get_dominant_role_for_cluster(row.values, job_roles_df['Job Roles'])

    # Extract top candidates from each cluster for the corresponding job role
    top_candidates_per_role = {}
    for cluster, job_role in dominant_roles.items():
        role_count_column = job_role + ' Count'
        cluster_df = stackoverflow_df[stackoverflow_df['Cluster'] == cluster]
        top_candidates = cluster_df.sort_values(by=[role_count_column, 'Owner Reputation', 'Gold Badges', 'Silver Badges', 'Bronze Badges'], ascending=False).head(10)
        top_candidates_per_role[job_role] = top_candidates

    # Save the top candidates to a CSV file for each job role
    # for role, candidates_df in top_candidates_per_role.items():
    #        print(candidates_df)
    #        candidates_df.to_csv(f'candidates_for_{role}122.csv', index=False)

        for role, candidates_df in top_candidates_per_role.items():
        # Convert the role name to lowercase and replace spaces with underscores
          role_lower_with_underscore = role.lower().replace(' ', '_')
          table_name = f'candidates{role_lower_with_underscore}'
          save_to_database(candidates_df, table_name)