import streamlit as st
import sqlite3
import smtplib
from email.message import EmailMessage

import sqlite3

def init_db():
    conn = sqlite3.connect('responses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            body_score INTEGER,
            emotions_score INTEGER,
            mind_score INTEGER,
            spirit_score INTEGER,
            total_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def append_to_google_sheet(name, email, scores, total_score):
    # Set up credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    import json
    from oauth2client.service_account import ServiceAccountCredentials

    service_account_info = st.secrets["google_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet (by name or URL)
    sheet = client.open("Energy Audit Responses").sheet1

    # Create row data
    row = [
        name,
        email,
        scores["Body"],
        scores["Emotions"],
        scores["Mind"],
        scores["Spirit"],
        total_score
    ]

    # Append row to the sheet
    sheet.append_row(row)

def save_response(name, email, scores, total_score):
    conn = sqlite3.connect('responses.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO responses (name, email, body_score, emotions_score, mind_score, spirit_score, total_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        email,
        scores["Body"],
        scores["Emotions"],
        scores["Mind"],
        scores["Spirit"],
        total_score
    ))
    conn.commit()
    conn.close()

# Initialise the database when the app starts
init_db()

# ----- Setup Email Secrets -----
email_address = st.secrets["email"]["address"]
email_password = st.secrets["email"]["password"]

# ----- Functions -----
def interpret_score(score):
    if score <= 3:
        return "Excellent energy management skills."
    elif score <= 6:
        return "Reasonable energy management skills."
    elif score <= 10:
        return "Significant energy management deficits."
    else:
        return "A full-fledged energy management crisis."

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_address
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)

def init_db():
    conn = sqlite3.connect('responses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            name TEXT,
            email TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_response(name, email, scores, total_score):
    conn = sqlite3.connect('responses.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO responses (name, email, body_score, emotions_score, mind_score, spirit_score, total_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        email,
        scores["Body"],
        scores["Emotions"],
        scores["Mind"],
        scores["Spirit"],
        total_score
    ))
    conn.commit()
    conn.close()

# ----- Initial Setup -----
init_db()

# ----- Streamlit UI -----
st.title("Are You Headed for an Energy Crisis?")
st.write("Check the statements that are true for you:")

categories = {
    "Body": [
        "I don’t regularly get at least seven to eight hours sleep...",
        "I frequently skip breakfast, or settle for something that isn’t nutritious.",
        "I don’t work out enough...",
        "I don’t take regular breaks during the day..."
    ],
    "Emotions": [
        "I frequently find myself feeling irritable or anxious...",
        "I don’t have enough time with my family and loved ones...",
        "I have too little time for activities I enjoy.",
        "I don’t stop frequently enough to express appreciation..."
    ],
    "Mind": [
        "I have difficulty focusing on one thing...",
        "I spend much of my day reacting to immediate crises...",
        "I don’t take enough time for reflection or strategy.",
        "I work in the evenings and on weekends..."
    ],
    "Spirit": [
        "I don’t spend enough time at work doing what I do best.",
        "There are gaps between what I value and how I spend my energy.",
        "My decisions are often influenced by external demands.",
        "I don’t invest enough time and energy in making a difference."
    ]
}

# Scoring
scores = {}
total_score = 0

for category, questions in categories.items():
    st.subheader(category)
    score = 0
    for q in questions:
        if st.checkbox(q, key=f"{category}_{q}"):
            score += 1
    scores[category] = score
    total_score += score

# Show results
# st.markdown("---")
# st.subheader("Your Results")
#for category, score in scores.items():
#    st.write(f"**{category} Score:** {score}")
#st.write(f"**Total Score:** {total_score}")

# Interpret score live with colour
#if total_score <= 3:
#    st.success("Excellent energy management skills.")
#elif total_score <= 6:
#    st.info("Reasonable energy management skills.")
#elif total_score <= 10:
#    st.warning("Significant energy management deficits.")
#else:
#    st.error("A full-fledged energy management crisis.")

st.markdown("### Enter your name and email address to receive your results via email. (Make sure to check your spam)")
# Form inputs
name = st.text_input("Your Name")
email = st.text_input("Your Email Address")

# Submit
if st.button("Submit"):
    if name and email:
        score_meaning = interpret_score(total_score)
        # Save to database
        save_response(name, email, scores, total_score)
        append_to_google_sheet(name, email, scores, total_score)
        # Create breakdown string
        score_breakdown = "\n".join([f"- {category}: {score}" for category, score in scores.items()])


        email_body = f"""Hi {name},

Thank you for completing the Energy Audit.

Your total score is: {total_score}
This means: {score_meaning}

Here’s how your scores break down by category:
{score_breakdown}
Note: The higher the score, the more that area is calling for your attention and intention.

We hope this gives you some helpful insight into your current energy levels. If you would like to improve your scores, reply to this email, and we can discuss your needs

Warm regards,
Lawrence
CEO Raw Energy | Finding Equilibrium | Wellbeing @ Work APAC
"""

        send_email(email, "Your Energy Audit Score", email_body)
        st.success("Form submitted successfully and email sent!")
    else:
        st.warning("Please enter both your name and email.")
