"""
Setup script: Initializes the FarewellVoting2026 Google Sheet
with correct tabs, headers, and sample data.
Run this ONCE before starting the app.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "FarewellVoting2026"

# ─── Sample Data (EDIT THESE with real names & emails) ───
# ─── Sample Data (EDIT THESE with real names & emails) ───
MR_CANDIDATES = ["Candidate 1", "Candidate 2", "Candidate 3"]
MISS_CANDIDATES = ["Candidate 4", "Candidate 5", "Candidate 6"]

# RollNumber, Name, Email, Role
USERS = [
    ["101", "Alice", "alice@example.com", "Voter"],
    ["102", "Bob", "bob@example.com", "Voter"],
    ["103", "Charlie", "charlie@example.com", "Voter"],
    ["104", "Diana", "diana@example.com", "Voter"],
    ["105", "Eve", "eve@example.com", "Voter"],
    ["200", "Admin", "admin@example.com", "Election Commissioner"],
]


def ensure_tab(spreadsheet, tab_name, existing_tabs, headers, data_rows=None, rows=200, cols=10):
    if tab_name in existing_tabs:
        ws = spreadsheet.worksheet(tab_name)
        print(f"  Found '{tab_name}' tab")
    else:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=rows, cols=cols)
        print(f"  + Created '{tab_name}' tab")

    all_values = ws.get_all_values()
    if not all_values or all_values[0] != headers:
        print(f"    Setting up headers & data...")
        ws.clear()
        payload = [headers]
        if data_rows:
            payload.extend(data_rows)
        ws.update(range_name="A1", values=payload)
        print(f"    Done ({len(payload)-1} rows)")
    else:
        print(f"    Already has {len(all_values)-1} rows")
    return ws


def main():
    print("Connecting to Google Sheets...")
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open(SHEET_NAME)
        print(f"Found spreadsheet: {SHEET_NAME}")
    except gspread.SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet '{SHEET_NAME}' not found!")
        return

    existing_tabs = [ws.title for ws in spreadsheet.worksheets()]
    print(f"Existing tabs: {existing_tabs}")

    # 1. Users tab (with Email instead of Phone)
    ensure_tab(spreadsheet, "Users", existing_tabs,
               ["RollNumber", "Name", "Email", "Role"], USERS)

    # 2. Candidates tab
    cand_rows = [["Mr Farewell", n] for n in MR_CANDIDATES] + [["Miss Farewell", n] for n in MISS_CANDIDATES]
    ensure_tab(spreadsheet, "Candidates", existing_tabs,
               ["Category", "Name"], cand_rows)

    # 3. Votes tab
    ensure_tab(spreadsheet, "Votes", existing_tabs,
               ["Voter", "MrVote", "MissVote", "Timestamp"])

    # 4. Extra Emails tab
    ensure_tab(spreadsheet, "Emails", existing_tabs,
               ["Email"], [["senior1@example.com"], ["senior2@example.com"]])

    # Cleanup old tabs
    for old_tab in ["Sheet1", "Participants"]:
        if old_tab in existing_tabs:
            try:
                spreadsheet.del_worksheet(spreadsheet.worksheet(old_tab))
                print(f"  Removed '{old_tab}'")
            except Exception:
                pass

    print("\n" + "=" * 50)
    print("SETUP COMPLETE!")
    print("=" * 50)
    print(f"URL: {spreadsheet.url}")
    print(f"\nRun: python -m streamlit run app.py")


if __name__ == "__main__":
    main()
