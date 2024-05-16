# Recruiter-System

Welcome to Hush-Hush Recruiter! Here's a sneak peek into what makes this project tick:

1. Data Fetching and Preparation:
Fetches user profile links via API calls, conducts web scraping for data extraction, and saves it into a CSV file. The data is stored in a PostgreSQL database for further processing.

2. Model Training and Testing:
Divides the fetched data into training, testing, and unseen datasets, then trains and evaluates a model for each job role. The trained models are saved in Pickle files for future use.

3. Candidate Selection and Assessment Process:
Utilizes the trained models to process candidate data and identify top candidates. Managers can send coding invitations through a designated interface, and eligible candidates receive coding test invitations via email.

4. Candidate Evaluation and Feedback:
Stores candidates' coding test responses and evaluations in a database table. Provides immediate feedback based on coding test results through the interface.

This project aims to optimize the recruitment workflow by automating candidate selection and assessment while ensuring confidentiality and efficiency throughout the process.
