import streamlit as st

import sqlite3

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

def save_response(name, email, score):
    conn = sqlite3.connect('responses.db')
    c = conn.cursor()
    c.execute('INSERT INTO responses (name, email, score) VALUES (?, ?, ?)', (name, email, score))
    conn.commit()
    conn.close()

init_db()


st.title("Are You Headed for an Energy Crisis?")
st.write("Check the statements that are true for you:")

# Define categories and questions
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

# Score tracking
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

st.markdown("---")
st.subheader("Your Results")

for category, score in scores.items():
    st.write(f"**{category} Score:** {score}")

st.write(f"**Total Score:** {total_score}")

# Interpret score
if total_score <= 3:
    st.success("Excellent energy management skills")
elif total_score <= 6:
    st.info("Reasonable energy management skills")
elif total_score <= 10:
    st.warning("Significant energy management deficits")
else:
    st.error("A full-fledged energy management crisis")

name = st.text_input("Your Name")
email = st.text_input("Your Email Address")

if st.button("Submit"):
    if name and email:
        # Save or send data here
        st.success("Form submitted successfully!")
        save_response(name, email, total_score)
        score_meaning = interpret_score(total_score)

        email_body = f"""Hi {name},

            Thank you for completing the Energy Audit.

            Your total score is: {total_score}
            This means: {score_meaning}

            We hope this gives you some helpful insight into your current energy levels.
            """

        send_email(email, "Your Energy Audit Score", email_body)

    else:
        st.warning("Please enter both your name and email.")

import smtplib
from email.message import EmailMessage

def interpret_score(score):
    if score <= 3:
        return "Excellent energy management skills."
    elif score <= 6:
        return "Reasonable energy management skills."
    elif score <= 10:
        return "Significant energy management deficits."
    else:
        return "A full-fledged energy management crisis."


import streamlit as st
email_address = st.secrets["email"]["address"]
email_password = st.secrets["email"]["password"]

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_address
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)

