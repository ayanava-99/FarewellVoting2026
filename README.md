# 🎓 Farewell 2026 — Mr. & Mrs. Farewell Voting App

A beautiful real-time voting app built with Streamlit + Google Sheets.

---

## 📋 Setup Guide

### Step 1: Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable **Google Sheets API** and **Google Drive API**
4. Go to **Credentials** → Create **Service Account**
5. Create a JSON key for the service account → download it
6. Rename the file to `credentials.json` and place it in this folder

### Step 2: Create the Google Sheet

Create a Google Sheet named **`FarewellVoting2026`** with **3 worksheets**:

#### Sheet 1: `Candidates`
| Category      | Name           |
|---------------|----------------|
| Mr Farewell   | Rahul Sharma   |
| Mr Farewell   | Amit Verma     |
| Mr Farewell   | Rohan Gupta    |
| Mrs Farewell  | Priya Singh    |
| Mrs Farewell  | Sneha Patel    |
| Mrs Farewell  | Ananya Reddy   |

#### Sheet 2: `Participants`
| Name            |
|-----------------|
| Student 1       |
| Student 2       |
| Student 3       |
| ... (all voters)|

#### Sheet 3: `Votes`
| Voter | MrVote | MrsVote | Timestamp |
|-------|--------|---------|-----------|
*(Leave this empty — votes will be appended automatically)*

> **Important:** The first row of each sheet must have the exact column headers shown above.

### Step 3: Share the Sheet

Share the Google Sheet with the **service account email** (found in `credentials.json` as `client_email`). Give it **Editor** access.

### Step 4: Install & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🗳️ Features

- **Secure Voting** — Each participant can vote only once
- **Separate Categories** — Mr. Farewell & Mrs. Farewell
- **Live Dashboard** — Bar charts, donut charts, and leader cards
- **Refresh Button** — Click to pull latest results from Google Sheets
- **Beautiful UI** — Gradient animations, glassmorphism, dark theme
