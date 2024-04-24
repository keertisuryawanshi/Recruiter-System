import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

# sender email and password
SENDER = os.getenv('RECRUITER_MAIL')
PASSWORD = os.getenv('RECRUITER_PASSWORD')

def send_email(receiver, subject, body):
    # Ensure that none of the parameters are None
    if not all([SENDER, receiver, subject, body]):
        print("One or more parameters are None. Please check.")
        return

    message = MIMEText(body)
    message["From"] = SENDER
    message["To"] = receiver
    message["Subject"] = subject

    try:
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.ehlo()
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, receiver, message.as_string())
        smtp_server.quit()
        print(f"Successfully sent email to {receiver}")
    except Exception as e:
        print(f"Unsuccessful in sending email. Error: {e}.")

# # Testing the function
# test_receiver = "demo@gmail.com"
# test_subject = "'Congratulations! You've been Selected for the Doodle Hiring Process'"
# test_body = """
# <html>
# <head>
#     <style>
#         body {
#             font-family: Arial, sans-serif;
#             margin: 0;
#             padding: 0;
#             color: #333333;
#         }
#         .container {
#             width: 100%;
#             max-width: 600px;
#             margin: 20px auto;
#             padding: 20px;
#             border: 1px solid #ddd;
#             border-radius: 5px;
#             box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
#         }
#         .header {
#             font-size: 18px;
#             margin-bottom: 10px;
#         }
#         .content {
#             margin-top: 20px;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">Coding Challenge</div>
#         <div class="content">
#             <p>Dear Candidate,</p>

#             <p>We're thrilled to announce that you've been selected for a coding challenge opportunity at Doodle! Below, you'll find the link to access the challenge. Once completed, we eagerly anticipate your feedback regarding the challenge.

#             <p>Link to the coding challenge: https://evaluation-ncivxdxcsrirout3r5s8kz.streamlit.app/</p>
#             <p>Link to the feedback page: http://http://127.0.0.1:5000/feedback_form/</p>

#             <p>Looking forward to meeting you soon.</p>

#             <p>Best regards,</p>
#             <p>Recruiter</p>
            
#         </div>
#     </div>
# </body>
# </html>
# """

# send_email(test_receiver, test_subject, test_body)
