import os
import sqlite3
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash  # flash for messaging
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()  # Loads .env variables into environment

app = Flask(__name__)

# Needed for flashing messages (keep this secret in production)
app.secret_key = "someRandomSecretKeyHere"

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
    1) Takes form data (email, company).
    2) Saves to SQLite.
    3) Sends an email via SendGrid dynamic template.
    4) Flashes a success or error message, then redirects back to home.
    """
    email = request.form.get('email')
    company = request.form.get('company')

    if not email or not company:
        flash("Missing email or company name.", "danger")
        return redirect(url_for('home'))

    # 1) Insert into SQLite DB
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO signups (email, company) VALUES (?, ?)', (email, company))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        flash("This email is already registered.", "warning")
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"Error saving to DB: {str(e)}", "danger")
        return redirect(url_for('home'))

    # 2) Send dynamic template email via SendGrid
    if SENDGRID_API_KEY:
        # Build the message
        message = Mail(
            from_email='your_verified_sender@datagift.app',  # must be verified in SendGrid
            to_emails=email
        )
        # Use your dynamic template
        message.template_id = 'd-b1925e2c902c4f39854855e222f38fb5'
        # Pass placeholders that your template expects, e.g. {{company}}
        message.dynamic_template_data = {
            "company": company
        }

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            # Optional: flash a message about the response, or debug info
            # flash(f"SendGrid response code: {response.status_code}", "info")
        except Exception as e:
            flash(f"Error sending email: {str(e)}", "danger")
    else:
        flash("Warning: No SENDGRID_API_KEY set, email not sent.", "warning")

    # 3) Everything went well, flash success
    flash("Thank you for signing up! Check your inbox for a welcome email.", "success")
    # Then redirect back to home (index.html)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
