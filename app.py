import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash  # for flashing messages
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables (so we can read SENDGRID_API_KEY, etc.)
load_dotenv()

app = Flask(__name__)
app.secret_key = "someRandomSecretKeyHere"  # Keep secret in production!

# 1) Read the SendGrid key from environment
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Print once on startup to confirm the app sees it
print("DEBUG: Starting app with SENDGRID_API_KEY =", SENDGRID_API_KEY)


@app.route('/')
def home():
    """Serve your main landing page (index.html)."""
    return render_template('index.html')


@app.route('/subscribe', methods=['POST'])
def subscribe():
    """
    1) Takes form data (email, company).
    2) Sends an email via SendGrid dynamic template (no DB).
    3) Flashes success or error message, then redirects back to home.
    """
    email = request.form.get('email')
    company = request.form.get('company')

    # Quick validation
    if not email or not company:
        flash("Missing email or company name.", "danger")
        return redirect(url_for('home'))

    # 2) Send dynamic template email via SendGrid
    if SENDGRID_API_KEY:
        print(f"DEBUG: Using SENDGRID_API_KEY='{SENDGRID_API_KEY}' inside /subscribe")
        
        message = Mail(
            from_email='datagift@datagift.app',  # Must be verified in SendGrid
            to_emails=email
        )
        message.template_id = 'd-b1925e2c902c4f39854855e222f38fb5'
        # Pass placeholders that your template expects, e.g. {{company}}
        message.dynamic_template_data = {
            "company": company
        }

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print("DEBUG: SendGrid response code =", response.status_code)
            # Optionally print full response if needed:
            # print("DEBUG: Full SendGrid response:", response.body)
        except Exception as e:
            print("DEBUG: Exception while sending via SendGrid:", e)
            flash(f"Error sending email: {str(e)}", "danger")
    else:
        print("DEBUG: No SENDGRID_API_KEY found in environment!")
        flash("Warning: No SENDGRID_API_KEY set, email not sent.", "warning")

    # 3) Flash success and redirect
    flash("Thank you for signing up! Check your inbox for a welcome email.", "success")
    return redirect(url_for('home'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
