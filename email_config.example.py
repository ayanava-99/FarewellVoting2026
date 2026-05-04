# ─── Email OTP Configuration ───
# Use a Gmail account to send OTPs.
# You need to enable 2-Step Verification on Google Account, then create an App Password:
#   1. Go to https://myaccount.google.com/apppasswords
#   2. Create an app password for "Mail"
#   3. Paste the 16-character password below

SENDER_EMAIL = "your_email@gmail.com"
SENDER_APP_PASSWORD = "your_app_password"  # 16-char app password (with spaces is fine)

# Set to False once you've configured the above
DEMO_MODE = True
