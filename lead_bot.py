import streamlit as st
import pandas as pd
import altair as alt
import datetime
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔐 CONFIG
openai.api_key = "sk-your-openai-key"  # Replace with your actual key
DATA_FILE = "streamlit_leads.csv"
YOUR_EMAIL = "tyagikhushbu4@gmail.com"
YOUR_APP_PASSWORD = "rlur hwoe egby rhlb"  # Use Gmail app password

# ✉️ Confirmation Email Function
def send_confirmation_email(to_email, name, interest, contact_date, contact_time, gpt_message):
    msg = MIMEMultipart()
    msg['From'] = YOUR_EMAIL
    msg['To'] = to_email
    msg['Subject'] = f"Thanks for connecting with us, {name}!"
    body = f"""
Hi {name},

Thank you for showing interest in "{interest}".
We’re excited to speak with you on {contact_date} at {contact_time}.

Here’s something for you:
"{gpt_message}"

Warm regards,  
The Connects Team
"""
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
        server.sendmail(YOUR_EMAIL, to_email, msg.as_string())

# 🌐 Page Setup
st.set_page_config(page_title="Connects", page_icon="🤝", layout="centered")

# 🎨 Custom Styling
st.markdown("""
    <style>
        body {
            background-color: #f5f7fb;
        }
        .stApp {
            background: linear-gradient(135deg, #ffffff 0%, #e6f0ff 100%);
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #1a1a1a;
            font-family: 'Segoe UI', sans-serif;
        }
        .css-18e3th9 {
            padding: 2rem 2rem 2rem 2rem;
        }
        button[kind="secondary"] {
            background-color: #ffffff;
            color: #3366cc;
            border: 1px solid #3366cc;
        }
        .stButton > button:hover {
            background-color: #3366cc;
            color: white;
        }
        .stDownloadButton button {
            background-color: #3366cc;
            color: white;
            border-radius: 8px;
        }
        .stDownloadButton button:hover {
            background-color: #264d99;
        }
        .footer {
            font-size: 12px;
            color: #666;
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# 🧠 App State Init
if not st.session_state.get("step"):
    st.session_state.step = 0
    st.session_state.data = {}

# 🔰 Header
st.markdown("<h1 style='text-align:center;'>🤝 Connects</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your smart assistant — here to connect you with what matters.</p>", unsafe_allow_html=True)
st.markdown("---")

# 📋 Lead Collection
steps = [
    ("Name", "👤 Your full name:"),
    ("Email", "📧 Email address:"),
    ("Company", "🏢 Company name:"),
    ("Interest", "💡 What are you interested in?"),
    ("Phone", "📞 Contact number:"),
    ("Location", "📍 Your location:")
]

for idx, (key, label) in enumerate(steps):
    if st.session_state.step == idx:
        st.session_state.data[key] = st.text_input(label)
        if st.session_state.data[key]:
            st.session_state.step += 1
        st.stop()

# Contact Date
if st.session_state.step == len(steps):
    st.session_state.data["Preferred Contact Date"] = st.date_input("📅 Preferred contact date:")
    st.session_state.step += 1
    st.stop()

# Contact Time
elif st.session_state.step == len(steps) + 1:
    st.session_state.data["Preferred Contact Time"] = st.time_input("⏰ Preferred contact time:")
    st.session_state.data["Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    df = pd.read_csv(DATA_FILE) if pd.io.common.file_exists(DATA_FILE) else pd.DataFrame(columns=st.session_state.data.keys())
    df = pd.concat([df, pd.DataFrame([st.session_state.data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    # GPT Response
    with st.spinner("🤖 Generating your personalized message..."):
        try:
            user_interest = st.session_state.data["Interest"]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful business assistant."},
                    {"role": "user", "content": f"Give a short, warm message to a client interested in '{user_interest}'."}
                ]
            )
            gpt_message = response["choices"][0]["message"]["content"]
        except Exception as e:
            gpt_message = "We're excited to help you with that! Our team will reach out soon."

    # Display GPT message
    st.success(f"🎉 Thank you {st.session_state.data['Name']}! Here's a message just for you:\n\n💬 {gpt_message}")

    # Send confirmation email
    send_confirmation_email(
        to_email=st.session_state.data["Email"],
        name=st.session_state.data["Name"],
        interest=st.session_state.data["Interest"],
        contact_date=st.session_state.data["Preferred Contact Date"],
        contact_time=str(st.session_state.data["Preferred Contact Time"]),
        gpt_message=gpt_message
    )

    # Recap
    st.markdown("### 🧾 Submission Summary")
    for k, v in st.session_state.data.items():
        st.markdown(f"- **{k}:** {v}")
    st.session_state.step += 1

# 🔄 Restart Option
elif st.session_state.step == len(steps) + 2:
    st.markdown("### 🔄 Want to submit another response?")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.data = {}

# 📊 Leads Overview (Admin Only)
st.markdown("---")
st.markdown("### 🔒 Admin Access")

admin_password = st.text_input("Enter admin password to view leads dashboard:", type="password")

if admin_password == "connects@ai2025":
    if pd.io.common.file_exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        st.download_button(
            label="📥 Download All Leads (CSV)",
            data=df.to_csv(index=False),
            file_name="connects_leads.csv",
            mime="text/csv"
        )

        if not df.empty and "Interest" in df.columns:
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    x="Interest:N",
                    y="count()",
                    color="Interest:N",
                    tooltip=["Interest", "count()"]
                )
                .properties(width=500, height=300)
            )
            st.altair_chart(chart)
    else:
        st.warning("No data available yet.")
else:
    st.info("Dashboard is restricted. Please enter the admin password to access this section.")

# 🔻 Footer
st.markdown("<hr><p class='footer' style='text-align:center;'>© 2025 Connects | Powered by Tempest AI</p>", unsafe_allow_html=True)
