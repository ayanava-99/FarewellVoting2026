import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import os
import time
import requests.exceptions

st.set_page_config(page_title="🎓 Farewell Voting 2026", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f.read(), unsafe_allow_html=True)

for key in ["logged_in","user_role","user_name","user_roll","otp_sent","otp_value","just_voted"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["logged_in","otp_sent","just_voted"] else ""

# ─── Retry wrapper ───
def with_retry(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except (ConnectionError, ConnectionAbortedError, ConnectionResetError,
                OSError, gspread.exceptions.APIError, requests.exceptions.ConnectionError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
                st.session_state.pop("_gsheet", None)
            else:
                raise e

# ─── Google Sheets ───
def get_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(os.path.dirname(__file__), "credentials.json"), scope)
    return gspread.authorize(creds)

def get_spreadsheet():
    if "_gsheet" not in st.session_state or st.session_state._gsheet is None:
        st.session_state._gsheet = get_client().open("FarewellVoting2026")
    return st.session_state._gsheet

def get_ws(name):
    try: return get_spreadsheet().worksheet(name)
    except:
        st.session_state._gsheet = None
        return get_spreadsheet().worksheet(name)

def load_users():
    return with_retry(lambda: pd.DataFrame(get_ws("Users").get_all_records()))

def load_candidates():
    def _l():
        df = pd.DataFrame(get_ws("Candidates").get_all_records())
        return (df[df["Category"].str.lower()=="mr farewell"]["Name"].tolist(),
                df[df["Category"].str.lower()=="miss farewell"]["Name"].tolist())
    return with_retry(_l)

def load_votes():
    def _l():
        d = get_ws("Votes").get_all_records()
        return pd.DataFrame(d) if d else pd.DataFrame(columns=["Voter","MrVote","MissVote","Timestamp"])
    return with_retry(_l)

def cast_vote(voter, mr_vote, miss_vote):
    with_retry(lambda: get_ws("Votes").append_row([voter, mr_vote, miss_vote, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]))

def has_voted(votes_df, roll):
    if votes_df.empty: return False
    return str(roll) in votes_df["Voter"].astype(str).values

# ═══════════════════════════════════════
# HERO BANNER
# ═══════════════════════════════════════
st.markdown("""
<div class="hero-banner">
    <div class="sparkle s1">✨</div><div class="sparkle s2">🌟</div><div class="sparkle s3">✨</div>
    <div class="sparkle s4">💫</div><div class="sparkle s5">⭐</div>
    <h1 class="hero-title">🎓 Farewell 2026</h1>
    <p class="hero-subtitle">Mr. & Miss Farewell Election</p>
    <p class="hero-tagline">Pick your star • Share the joy • Make memories ✨</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# LOGIN SCREEN
# ═══════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("")
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div class="login-card">
            <div class="login-icon">🔐</div>
            <h2 class="login-title">Welcome, Voter!</h2>
            <p class="login-sub">Enter your roll number to get started</p>
            <p class="login-sub" style="margin-top:0.8rem; font-style:italic; font-size:0.85rem; color:#C084FC;">"Not all heroes wear capes… some win farewell titles 😎"</p>
            <p class="login-sub" style="margin-top:1rem; font-size:0.75rem; color:#6b7280; font-style:italic;">Powered by ECI - Election Commission of India 🇮🇳<br>In association with Mtech AI batch 2027 🤖</p>
        </div>
        """, unsafe_allow_html=True)

        roll_input = st.text_input("📝 Roll Number", placeholder="Enter your roll number", key="roll_input", label_visibility="collapsed")

        if not st.session_state.otp_sent:
            if st.button("📧  Send OTP to Email", type="primary", use_container_width=True):
                if not roll_input.strip():
                    st.error("Please enter your roll number.")
                else:
                    try:
                        users_df = load_users()
                        users_df["RollNumber"] = users_df["RollNumber"].astype(str).str.strip().str.replace(r'\.0$','',regex=True).str.upper()
                        roll_clean = roll_input.strip().replace(".0","").upper()
                        match = users_df[users_df["RollNumber"]==roll_clean]
                        if match.empty:
                            st.error("❌ Roll number not found.")
                        else:
                            from otp_service import generate_otp, send_otp
                            otp = generate_otp()
                            email = str(match.iloc[0]["Email"]).strip()
                            success, msg = send_otp(email, otp)
                            if success:
                                st.session_state.otp_value = otp
                                st.session_state.otp_sent = True
                                parts = email.split("@")
                                st.session_state._email_display = parts[0][:2]+"***@"+parts[1] if "@" in email else "***"
                                st.session_state._is_demo = (msg=="DEMO")
                                st.session_state._user_data = {"name":str(match.iloc[0]["Name"]).upper(),"role":match.iloc[0]["Role"],"roll":roll_clean}
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
        else:
            email_hint = st.session_state.get("_email_display","***")
            st.success(f"✅ OTP sent to **{email_hint}**")
            if st.session_state.get("_is_demo", True):
                st.info(f"🔑 Demo OTP: **{st.session_state.otp_value}**")
            else:
                st.info("📧 Check your email inbox")

            otp_input = st.text_input("🔢 Enter 6-digit OTP", placeholder="Enter OTP", key="otp_input", max_chars=6, label_visibility="collapsed")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Verify", type="primary", use_container_width=True):
                    if otp_input == st.session_state.otp_value:
                        st.session_state.logged_in = True
                        ud = st.session_state._user_data
                        st.session_state.user_name = ud["name"]
                        st.session_state.user_role = ud["role"]
                        st.session_state.user_roll = ud["roll"]
                        st.rerun()
                    else:
                        st.error("❌ Wrong OTP")
            with c2:
                if st.button("🔄 Resend", use_container_width=True):
                    from otp_service import generate_otp, send_otp
                    otp = generate_otp()
                    email = ""
                    try:
                        users_df = load_users()
                        users_df["RollNumber"] = users_df["RollNumber"].astype(str).str.strip().str.replace(r'\.0$','',regex=True).str.upper()
                        m = users_df[users_df["RollNumber"]==st.session_state._user_data["roll"].upper()]
                        if not m.empty: email = str(m.iloc[0]["Email"]).strip()
                    except: pass
                    success, msg = send_otp(email, otp)
                    if success:
                        st.session_state.otp_value = otp
                        st.session_state._is_demo = (msg=="DEMO")
                    st.rerun()
    st.stop()

# ═══════════════════════════════════════
# LOGGED IN
# ═══════════════════════════════════════
role = st.session_state.user_role
is_commissioner = role.lower() == "election commissioner"

# Top bar
role_color = "#FFD700" if is_commissioner else "#22C55E"
role_label = "🛡️ Election Commissioner" if is_commissioner else "🗳️ Voter"
st.markdown(f"""
<div class="topbar">
    <div class="topbar-user">
        <span class="topbar-avatar">👤</span>
        <div>
            <span class="topbar-name">{st.session_state.user_name.upper()}</span>
            <span class="topbar-role" style="color:{role_color};">{role_label}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_logout, _ = st.columns([1, 5])
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ═══════════════════════════════════════
# VOTER VIEW
# ═══════════════════════════════════════
if not is_commissioner:
    votes_df = load_votes()

    if has_voted(votes_df, st.session_state.user_roll) or st.session_state.just_voted:
        aladin_img_html = ""
        try:
            import base64
            with open("aladin.jpg", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            aladin_img_html = f'<div style="margin: 1.5rem 0;"><img src="data:image/jpeg;base64,{b64}" style="max-width:100%; width:280px; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.4); border:2px solid rgba(34,197,94,0.3);"></div>'
        except Exception as e:
            pass

        st.markdown(f"""
        <div class="thankyou-screen">
            <div class="thankyou-confetti">🎊</div>
            <div class="thankyou-icon">✅</div>
            <h1 class="thankyou-title">Thank You, {st.session_state.user_name.upper()}!</h1>
            <p class="thankyou-sub" style="color:#C084FC; font-weight:600; font-size:1.1rem;">Your vote has been received… and is 100% Aladeen approved 😎</p>
            {aladin_img_html}
            <div class="thankyou-divider" style="margin-top:0;"></div>
            <p class="thankyou-msg">
                Your voice matters! The results will be announced<br>
                by the Election Commissioner at the farewell event. 🎓
            </p>
            <div class="thankyou-badge">
                <span>🗳️</span> Verified Voter
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── VOTING SCREEN ──
        try:
            mr_candidates, miss_candidates = load_candidates()
        except Exception as e:
            st.error(f"Could not load candidates: {e}")
            st.stop()

        st.markdown('<div class="section-header">🗳️ Cast Your Vote</div>', unsafe_allow_html=True)

        col_mr, col_mrs = st.columns(2)
        with col_mr:
            st.markdown("""
            <div class="vote-card mr-card">
                <div class="card-badge">👑</div>
                <h3>Mr. Farewell</h3>
                <p class="card-hint">Select one candidate</p>
            </div>
            """, unsafe_allow_html=True)
            mr_opts = [c.upper() for c in mr_candidates]
            mr_choice = st.radio("Mr. Farewell", mr_opts, key="mr_vote", label_visibility="collapsed")

        with col_mrs:
            st.markdown("""
            <div class="vote-card mrs-card">
                <div class="card-badge">👸</div>
                <h3>Miss Farewell</h3>
                <p class="card-hint">Select one candidate</p>
            </div>
            """, unsafe_allow_html=True)
            miss_opts = [c.upper() for c in miss_candidates]
            miss_choice = st.radio("Miss Farewell", miss_opts, key="miss_vote", label_visibility="collapsed")

        st.markdown("---")

        # Confirmation summary
        st.markdown(f"""
        <div class="confirm-box">
            <h4>📋 Your Selection</h4>
            <div class="confirm-row"><span>👑 Mr. Farewell</span><strong>{mr_choice}</strong></div>
            <div class="confirm-row"><span>👸 Miss Farewell</span><strong>{miss_choice}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        col_b, _, _ = st.columns([2, 1, 1])
        with col_b:
            if st.button("🗳️  Submit My Vote", type="primary", use_container_width=True):
                cast_vote(st.session_state.user_roll, mr_choice, miss_choice)
                st.session_state.just_voted = True
                st.balloons()
                st.rerun()

# ═══════════════════════════════════════
# COMMISSIONER VIEW
# ═══════════════════════════════════════
else:
    if st.session_state.get("results_declared", False):
        st.markdown('<div class="hero-banner"><h1 class="hero-title" style="font-size:4rem;">🏆 Official Results 🏆</h1><p class="hero-subtitle">Farewell 2026</p></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="winner-display" style="gap:3rem; margin-top:2rem; margin-bottom:3rem;">
            <div class="winner-card mr-winner" style="padding:4rem 2rem; transform:scale(1.02);">
                <div class="winner-crown" style="font-size:5rem;">👑</div>
                <p class="winner-label" style="font-size:1.2rem;">MR. FAREWELL 2026</p>
                <h2 class="winner-name" style="font-size:3rem;">{st.session_state.mr_winner_name}</h2>
                <p class="winner-votes" style="font-size:1.2rem;">{st.session_state.mr_winner_votes} votes</p>
            </div>
            <div class="winner-card mrs-winner" style="padding:4rem 2rem; transform:scale(1.02);">
                <div class="winner-crown" style="font-size:5rem;">👸</div>
                <p class="winner-label" style="font-size:1.2rem;">MISS FAREWELL 2026</p>
                <h2 class="winner-name" style="font-size:3rem;">{st.session_state.miss_winner_name}</h2>
                <p class="winner-votes" style="font-size:1.2rem;">{st.session_state.miss_winner_votes} votes</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        col_bk, _ = st.columns([1, 4])
        with col_bk:
            if st.button("⬅️ Back to Dashboard", use_container_width=True):
                st.session_state.results_declared = False
                st.rerun()
        st.stop()

    tab1, tab2 = st.tabs(["📊 Live Results", "👥 Voters"])

    try:
        mr_candidates, miss_candidates = load_candidates()
    except Exception as e:
        st.error(f"Could not load candidates: {e}")
        st.stop()

    with tab1:
        st.markdown('<div class="section-header">📊 Live Election Dashboard</div>', unsafe_allow_html=True)

        col_r, col_s = st.columns([1, 3])
        with col_r:
            if st.button("🔄 Refresh", type="primary", use_container_width=True):
                st.session_state.pop("_gsheet", None)
                st.rerun()

        votes_df = load_votes()
        total = len(votes_df)
        users_df = load_users()
        voter_count = len(users_df[users_df["Role"].str.lower()=="voter"])

        with col_s:
            c1,c2,c3 = st.columns(3)
            c1.metric("Votes Cast", total, delta=f"{total}/{voter_count}")
            c2.metric("Turnout", f"{(total/voter_count*100) if voter_count else 0:.0f}%")
            c3.metric("Remaining", voter_count - total)

        if total == 0:
            st.markdown('<div class="info-card"><h3>📭 No votes yet</h3><p>Waiting for voters...</p></div>', unsafe_allow_html=True)
        else:
            colors_mr = ["#FF6B6B","#FF8E8E","#FFB4B4","#FFD4D4","#FFECEC"]
            colors_mrs = ["#A855F7","#C084FC","#D8B4FE","#E9D5FF","#F3E8FF"]

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="result-title">👑 Mr. Farewell</div>', unsafe_allow_html=True)
                mr_c = votes_df["MrVote"].value_counts().reset_index()
                mr_c.columns = ["Candidate","Votes"]
                ldr = mr_c.iloc[0] if not mr_c.empty else None
                if ldr is not None:
                    st.markdown(f'<div class="leader-card mr-leader"><span class="leader-emoji">🏆</span>'
                                f'<span class="leader-name">{ldr["Candidate"]}</span>'
                                f'<span class="leader-votes">{ldr["Votes"]} votes</span></div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="result-title">👸 Miss Farewell</div>', unsafe_allow_html=True)
                miss_c = votes_df["MissVote"].value_counts().reset_index()
                miss_c.columns = ["Candidate","Votes"]
                ldr2 = miss_c.iloc[0] if not miss_c.empty else None
                if ldr2 is not None:
                    st.markdown(f'<div class="leader-card mrs-leader"><span class="leader-emoji">🏆</span>'
                                f'<span class="leader-name">{ldr2["Candidate"]}</span>'
                                f'<span class="leader-votes">{ldr2["Votes"]} votes</span></div>', unsafe_allow_html=True)

            # Donut charts
            st.markdown("---")
            st.markdown('<div class="section-header">📈 Vote Share</div>', unsafe_allow_html=True)
            cd1, cd2 = st.columns(2)
            with cd1:
                fp1 = go.Figure(go.Pie(labels=mr_c["Candidate"],values=mr_c["Votes"],hole=0.55,
                                       marker=dict(colors=colors_mr[:len(mr_c)]),textinfo="label+percent"))
                fp1.update_layout(title=dict(text="Mr. Farewell",font=dict(color="#FF6B6B",size=18)),
                                  plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#FAFAFA"),height=340,showlegend=False,margin=dict(l=20,r=20,t=50,b=20))
                st.plotly_chart(fp1, use_container_width=True)
            with cd2:
                fp2 = go.Figure(go.Pie(labels=miss_c["Candidate"],values=miss_c["Votes"],hole=0.55,
                                       marker=dict(colors=colors_mrs[:len(miss_c)]),textinfo="label+percent"))
                fp2.update_layout(title=dict(text="Miss Farewell",font=dict(color="#A855F7",size=18)),
                                  plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#FAFAFA"),height=340,showlegend=False,margin=dict(l=20,r=20,t=50,b=20))
                st.plotly_chart(fp2, use_container_width=True)

            with st.expander("📋 Full Vote Log"):
                st.dataframe(votes_df, use_container_width=True, hide_index=True)

            # ─── DECLARE RESULTS ───
            st.markdown("---")
            st.markdown('<div class="section-header">🏆 Declare Results</div>', unsafe_allow_html=True)

            mr_winner = mr_c.iloc[0]["Candidate"].upper() if not mr_c.empty else "TBD"
            mr_winner_votes = mr_c.iloc[0]["Votes"] if not mr_c.empty else 0
            miss_winner = miss_c.iloc[0]["Candidate"].upper() if not miss_c.empty else "TBD"
            miss_winner_votes = miss_c.iloc[0]["Votes"] if not miss_c.empty else 0

            st.markdown(f"""
            <div class="winner-display">
                <div class="winner-card mr-winner">
                    <div class="winner-crown">👑</div>
                    <p class="winner-label">MR. FAREWELL 2026</p>
                    <h2 class="winner-name">{mr_winner}</h2>
                    <p class="winner-votes">{mr_winner_votes} votes</p>
                </div>
                <div class="winner-card mrs-winner">
                    <div class="winner-crown">👸</div>
                    <p class="winner-label">MISS FAREWELL 2026</p>
                    <h2 class="winner-name">{miss_winner}</h2>
                    <p class="winner-votes">{miss_winner_votes} votes</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if "results_declared" not in st.session_state:
                st.session_state.results_declared = False

            col_d, _ = st.columns([2, 2])
            with col_d:
                if st.button("🏆  Declare Results & Email Everyone", type="primary", use_container_width=True):
                    from otp_service import send_results_email
                    all_users = load_users()
                    voter_emails = all_users[all_users["Role"].str.lower()=="voter"]["Email"].tolist()
                    
                    try:
                        extra_df = pd.DataFrame(get_ws("Emails").get_all_records())
                        extra_emails = extra_df["Email"].tolist() if "Email" in extra_df.columns else []
                    except:
                        extra_emails = []

                    all_emails = list(set([str(e).strip() for e in voter_emails + extra_emails if str(e).strip() and "@" in str(e)]))

                    sent_count = 0
                    fail_count = 0
                    progress = st.progress(0, text="Sending emails to voters & candidates...")
                    for i, email in enumerate(all_emails):
                        ok, _ = send_results_email(email, mr_winner, miss_winner, mr_winner_votes, miss_winner_votes)
                        if ok: sent_count += 1
                        else: fail_count += 1
                        progress.progress((i+1)/len(all_emails), text=f"Sent {i+1}/{len(all_emails)}")
                        time.sleep(0.5)  # Rate limit
                    progress.empty()
                    
                    st.session_state.mr_winner_name = mr_winner
                    st.session_state.mr_winner_votes = mr_winner_votes
                    st.session_state.miss_winner_name = miss_winner
                    st.session_state.miss_winner_votes = miss_winner_votes
                    st.session_state.results_declared = True
                    st.rerun()

    with tab2:
        st.markdown('<div class="section-header">👥 Voter Status</div>', unsafe_allow_html=True)
        if st.button("🔄 Refresh Voters"): st.rerun()
        users_df = load_users()
        votes_df = load_votes()
        voters = users_df[users_df["Role"].str.lower()=="voter"]
        rows = []
        for _, row in voters.iterrows():
            voted = str(row["RollNumber"]) in votes_df["Voter"].astype(str).values if not votes_df.empty else False
            rows.append({"Roll":row["RollNumber"],"Name":str(row["Name"]).upper(),"Email":row["Email"],"Status":"✅ Voted" if voted else "⏳ Pending"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Footer
st.markdown('<div class="footer"><p>Made with ❤️ for Farewell 2026 🎓<br><span style="font-size:0.75rem; color:#6b7280; font-style:italic;">Powered by ECI - Election Commission of India 🇮🇳<br>In association with Mtech AI batch 2027 🤖</span></p></div>', unsafe_allow_html=True)
