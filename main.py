import streamlit as st
import openai
import os
from openai import OpenAI

st.title("Casino & Betting Push Notification Generator")

# Input fields
geo = st.text_input("Geo (Geographic Location)", value='United Kingdom')
holiday_name = st.text_input("Holiday Name (if any)", value='World Cup')
offer = st.text_input("Offer (Value of Bonus Code or Discount)", value=20)
bonus_code = st.text_input("Bonus Code (if any)", value='CUP20')
language = st.text_input("Language", value='English')
currency = st.text_input("Currency (if any)", value='%')
push_length = st.text_input('Push length', value=30)
push_num = st.text_input('Number of push notifications', value=5)
emoji = st.selectbox(
    'Do you need emojis in push?',
    ('Yes', 'No')
)

client = OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

# Function to generate push notifications
def generate_push_notifications(geo, holiday_name, offer, bonus_code, language, currency, push_length, push_num, emoji):
    prompt = f"""
    Task: Write short, creative push notifications for a casino and betting project. Notifications should be engaging, use wordplay, and incorporate humor to capture attention. Each notification must be based on the following parameters provided:

    Geo: The geographic location of the target audience.
    Holiday Name: The name of a holiday if there is one, to make the message relevant to current events.
    Offer: The actual value of the bonus code or discount being offered.
    Bonus Code: A specific code to be used if there is one.
    Language: The language in which the notification should be written.
    Currency: The currency relevant to the offer, if applicable.

    Examples:
    Don't miss this limited-time offer!
    Brug kampagnekoden THU for at få en 50% bonus op til hele 200 + 100 gratis spins!
    Use SPIN code today and get up to 100 FREE SPINS for a perfect Monday!

    Guidelines:
    1. Notifications should be concise and compelling.
    2. Incorporate playful language and humor where appropriate.
    3. Ensure the message aligns with the parameters given for each notification.
    4. Aim to capture the reader's interest quickly and motivate them to take action.
    5. Each push notification should be equal or less than {push_length} characters.
    {"6. Please do not use emojis." if emoji == 'No' else "You can use emojis"}

    Generate {push_num} push notifications in {language} language, using these placeholders:

    1. Geo: {geo}
    2. Holiday Name: {holiday_name}
    3. Offer: {offer}
    4. Bonus Code: {bonus_code}
    5. Language: {language}
    6. Currency: {currency}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a creative copywriter specializing in short, engaging push notifications."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        max_tokens=int(push_num) * int(push_length)
    )
    notifications = chat_completion.choices[0].message.content
    return notifications


# Button to generate notifications
if st.button("Generate Push Notifications"):
    if geo and holiday_name and offer and bonus_code and language and currency:
        notifications = generate_push_notifications(geo, holiday_name, offer, bonus_code, 
            language, currency, push_length, push_num, emoji)
        st.text_area("Generated Push Notifications", notifications, height=300)
    else:
        st.warning("Please fill in all input fields to generate push notifications.")

