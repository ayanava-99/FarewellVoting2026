"""
OTP sending module via Email (Gmail SMTP — completely free).
Configure your Gmail credentials in email_config.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(recipient_email, otp, sender_email, sender_password):
    """Send OTP via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎓 Farewell 2026 — Your Voting OTP"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    html_body = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif; max-width:480px; margin:auto;
                background:linear-gradient(135deg,#1a1d29,#0e1117); border-radius:16px;
                padding:32px; color:#fafafa;">
        <h2 style="text-align:center; margin:0 0 8px;">🎓 Farewell 2026</h2>
        <p style="text-align:center; color:#9ca3af; margin:0 0 24px;">Mr. & Miss Farewell Election</p>
        <div style="background:linear-gradient(135deg,#ff6b6b22,#a855f722); border-radius:12px;
                    padding:24px; text-align:center; border:1px solid #ff6b6b33;">
            <p style="color:#c9cdd3; margin:0 0 8px; font-size:14px;">Your One-Time Password</p>
            <h1 style="margin:0; font-size:36px; letter-spacing:8px;
                       background:linear-gradient(135deg,#ff6b6b,#a855f7);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                {otp}
            </h1>
            <p style="color:#6b7280; margin:12px 0 0; font-size:12px;">Valid for this session only</p>
        </div>
        <p style="color:#6b7280; font-size:12px; text-align:center; margin:24px 0 0;">
            If you didn't request this, please ignore this email.<br>
            <span style="font-size:10px; font-style:italic;">Powered by ECI - Election Commission of India<br>In association with Mtech AI batch 2027</span>
        </p>
    </div>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "OTP sent to your email!"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail authentication failed. Check email_config.py (use App Password, not your regular password)"
    except Exception as e:
        return False, f"Email error: {str(e)}"


def send_otp(recipient_email, otp):
    """Main function — checks config for demo/real mode."""
    from email_config import SENDER_EMAIL, SENDER_APP_PASSWORD, DEMO_MODE

    if DEMO_MODE or SENDER_EMAIL == "your_email@gmail.com":
        return True, "DEMO"

    return send_otp_email(recipient_email, otp, SENDER_EMAIL, SENDER_APP_PASSWORD)


def send_results_email(recipient_email, mr_winner, miss_winner, mr_votes, miss_votes):
    """Send election results announcement email."""
    from email_config import SENDER_EMAIL, SENDER_APP_PASSWORD, DEMO_MODE

    if DEMO_MODE or SENDER_EMAIL == "your_email@gmail.com":
        return True, "DEMO"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎓 Farewell 2026 — Results Announced!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    html_body = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif; max-width:520px; margin:auto;
                background:linear-gradient(135deg,#1a1d29,#0e1117); border-radius:20px;
                padding:36px; color:#fafafa;">
        <h1 style="text-align:center; margin:0 0 4px; font-size:28px;">🎓 Farewell 2026</h1>
        <p style="text-align:center; color:#9ca3af; margin:0 0 6px; font-size:14px;">Mr. & Miss Farewell Election</p>
        <p style="text-align:center; margin:0 0 28px;">
            <span style="background:linear-gradient(135deg,#ff6b6b,#a855f7); -webkit-background-clip:text;
                         -webkit-text-fill-color:transparent; font-weight:700; font-size:18px;">
                🏆 Results Declared! 🏆
            </span>
        </p>

        <div style="background:linear-gradient(135deg,#ff6b6b15,#ff6b6b08); border-radius:14px;
                    padding:24px; text-align:center; border:1px solid #ff6b6b25; margin-bottom:16px;">
            <p style="color:#ff8e8e; margin:0 0 4px; font-size:13px; text-transform:uppercase; letter-spacing:2px;">
                👑 Mr. Farewell 2026
            </p>
            <h2 style="margin:0; font-size:26px; color:#FAFAFA; font-weight:800;">{mr_winner}</h2>
            <p style="color:#6b7280; margin:8px 0 0; font-size:13px;">{mr_votes} votes</p>
        </div>

        <div style="background:linear-gradient(135deg,#a855f715,#a855f708); border-radius:14px;
                    padding:24px; text-align:center; border:1px solid #a855f725; margin-bottom:24px;">
            <p style="color:#c084fc; margin:0 0 4px; font-size:13px; text-transform:uppercase; letter-spacing:2px;">
                👸 Miss Farewell 2026
            </p>
            <h2 style="margin:0; font-size:26px; color:#FAFAFA; font-weight:800;">{miss_winner}</h2>
            <p style="color:#6b7280; margin:8px 0 0; font-size:13px;">{miss_votes} votes</p>
        </div>

        <div style="text-align:center; padding:16px; background:rgba(255,255,255,0.03);
                    border-radius:12px; border:1px solid rgba(255,255,255,0.06);">
            <p style="color:#9ca3af; margin:0 0 10px; font-size:13px; font-style:italic;">
                "You came, you saw, you conquered hearts! ✨"
            </p>
            <p style="color:#9ca3af; margin:0; font-size:13px;">
                🎊 Congratulations to the winners! 🎊<br>
                <span style="color:#6b7280; font-size:12px;">Thank you for being part of this celebration.</span>
            </p>
        </div>

        <p style="color:#4b5060; font-size:11px; text-align:center; margin:20px 0 0;">
            Made with ❤️ for Farewell 2026<br>
            <span style="font-size:10px; font-style:italic;">Powered by ECI - Election Commission of India<br>In association with Mtech AI batch 2027</span>
        </p>
    </div>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
        return True, "Sent!"
    except Exception as e:
        return False, str(e)
