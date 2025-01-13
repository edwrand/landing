import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file contents into environment variables


app = Flask(__name__)

# Set your SendGrid key as an environment var: SENDGRID_API_KEY = '...'
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

DB_NAME = "datagift.db"

def init_db():
    """Create the signups table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            company TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.before_first_request
def setup_db():
    """Ensure the table is created before handling any requests."""
    init_db()

@app.route('/')
def home():
    """Serve your main landing page (index.html)."""
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """
    Single endpoint:
    1) Takes form data (email, company).
    2) Stores in SQLite.
    3) Sends an email via SendGrid.
    4) Returns a quick HTML "thank you" (or JSON).
    """
    email = request.form.get('email')
    company = request.form.get('company')

    if not email or not company:
        return "<h3>Missing email or company</h3>", 400

    # 1) Store in SQLite
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO signups (email, company) VALUES (?, ?)', (email, company))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return "<h3>This email is already registered.</h3>", 409
    except Exception as e:
        return f"<h3>Error saving to DB: {str(e)}</h3>", 500

    # 2) Send a welcome email with SendGrid
    if SENDGRID_API_KEY:
        message = Mail(
            from_email='your_verified_sender@datagift.app',  # Must match a verified sender in SendGrid
            to_emails=email,
            subject='Welcome to DataGift Early Access!',
            html_content=f'''
                <h1>Thanks for signing up, {company}!</h1>
                <p>We appreciate your interest in DataGift. Check your inbox for updates and let us know if you have any questions.</p>
                <p>- The DataGift Team</p>
            '''
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print("SendGrid response code:", response.status_code)
        except Exception as e:
            print("Error sending email with SendGrid:", e)
    else:
        print("Warning: No SENDGRID_API_KEY set, email won't be sent.")

    # 3) Return a simple "Thank You" message (HTML)
    #    Alternatively, you could return JSON or redirect somewhere else.
    return """
    <html>
      <head>
        <title>Thank You!</title>
      </head>
      <body style="font-family: sans-serif; margin: 2rem;">
        <h2>Subscription Complete</h2>
        <p>Thank you for signing up, check your inbox for our welcome email!</p>
        <p><a href="/">Back to Home</a></p>
      </body>
    </html>
    """, 200

if __name__ == '__main__':
    # Heroku uses PORT env var
    import sys
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
