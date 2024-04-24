from flask import Flask, jsonify, redirect, render_template, request, url_for
import pandas as pd
import sys

sys.path.append('C:\\Users\\Keertisuryawanshi\\Desktop\\Python_Group 9\\evaluation_system')
from algopickle import get_top_candidates

sys.path.append('C:\\Users\\Keertisuryawanshi\\Desktop\\Python_Group 9\\notification_system')
from hushushmail import send_email

sys.path.append('C:\\Users\\Keertisuryawanshi\\Desktop\\Python_Group 9\\database')
from connection import engine

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        job_role = request.form['job_role']
        
        candidates = get_top_candidates(job_role) #Processes the candidates and saves them to the database
        
        table_name = f'candidates_{job_role.replace(" ", "_").lower()}'
        print(table_name)
        
        #query for fetching data from the database for the selected job role
        query = f"SELECT * FROM {table_name} LIMIT 10;"
        print(query)
        
        candidates_df = pd.read_sql(query, engine)
        print(candidates_df)
        
        candidates = candidates_df.to_dict(orient='records')
        print(candidates)
        
        return render_template('index.html', job_role=job_role, candidates=candidates)
    return render_template('index.html')


@app.route('/send_emails', methods=['POST'])
def send_emails():
    if request.method == 'POST':
        job_role = request.form['job_role']
        table_name = f'candidates_{job_role.replace(" ", "_").lower()}'

        #selecting email column from data 

        query = f'SELECT owner_email_address FROM {table_name} LIMIT 10;'
        print(query)
        candidates_emails_df = pd.read_sql(query, engine)
        print(candidates_emails_df)
        candidates_emails = candidates_emails_df['owner_email_address'].tolist()

        #sending email to each candidate 

        for email in candidates_emails:
            subject = "'Congratulations! You've been Selected for the Doodle Hiring Process'"
            body = """
                Dear Candidate,

                We're thrilled to announce that you've been selected for a coding challenge opportunity at Doodle! Below, you'll find the link to access the challenge. Once completed, we eagerly anticipate your feedback regarding the challenge.

                Link to the coding challenge: https://evaluation-ncivxdxcsrirout3r5s8kz.streamlit.app/
                Link to the feedback page: http://127.0.0.1:5000/feedback_form

                Looking forward to meeting you soon.

                Best regards,
                Recruiter
            """
            send_email(email, subject, body)

        return redirect(url_for('index'))

@app.route('/feedback_form')
def feedback_form():
    return render_template('feedback_form.html')

if __name__ == '__main__': 
    app.run(debug=True)
    