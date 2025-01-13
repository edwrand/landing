import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# For Heroku, set your SendGrid API key in Config Vars:
# SENDGRID_API_KEY = 'your-api-key-here'
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

@app.route('/')
def home():
    # Renders your landing page (index.html)
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Receives form data: email & company, saves to DB, sends a welcome email."""
    email = request.form.get('email')
    company = request.form.get('company')

    if not email or not company:
        return jsonify({"error": "Missing email or company"}), 400

    # Save to SQLite
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO signups (email, company) VALUES (?, ?)', (email, company))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Send welcome email with SendGrid
    if SENDGRID_API_KEY is None:
        print("Warning: SENDGRID_API_KEY is not set. Email won't be sent.")
    else:
        message = Mail(
            from_email='your_verified_sender@datagift.app',
            to_emails=email,
            subject='Welcome to DataGift Early Access!',
            html_content=f'''
            <h1>Thanks for signing up!</h1>
            <p>We appreciate your interest in DataGift, <strong>{company}</strong>.</p>
            <p>Please feel free to reply with any questions or feedback.</p>
            <p>Best,<br/>DataGift Team</p>
            '''
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print("SendGrid response:", response.status_code)
        except Exception as e:
            print("Error sending email with SendGrid:", e)

    return jsonify({"success": True, "message": "Subscription complete"}), 200

if __name__ == '__main__':
    # Ensure the DB is ready
    init_db()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
