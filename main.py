import streamlit as st
import openai
import os
from openai import OpenAI

st.title("Casino & Betting Push Notification Generator")

# Input fields
geo = st.text_input("Geo (Geographic Location)", value='United Kingdom')
holiday_name = st.text_input("Holiday Name (if any)", value='World Cup')
offer = st.text_input("Offer (Value of Bonus Code or Discount)", value=20)
currency = st.text_input("Currency (if any)", value='%')
bonus_code = st.text_input("Bonus Code (if any)", value='CUP20')
language = st.text_input("Language", value='English')
push_len = st.text_input('Title length', value=30)
description_len = st.text_input('Description length', value=40)
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

    Format the response as a JSON array with each notification having a "title" and "description".

    Format:
    [
        {{
            "title": "title_1"
            "description": "description_1"
        }}
    ]

    Example:
    [
        {{
            "title": "BLACK FRIDAY BONUS!"
            "desctiption": "Pouijte kd BLACKFRIDAY a zskejte 50% up to 2500 CZK + 50 Free Spins"
        }},
        {{
            "title": "Friday bonus: 250 for you",
            "description": "Make a deposit on Friday and get a 50% BONUS up to 250 + 100 FREE SPINS!"
        }},
        {{
            "title": "Limited-Time Offer",
            "description": "Don't miss out on this exclusive deal - get a 50% bonus up to 200 + 100 free spins with code THU!"
        }}
    ]

    Guidelines:
    1. Notifications should be concise and compelling.
    2. Incorporate playful language and humor where appropriate.
    3. Ensure the message aligns with the parameters given for each notification.
    4. Aim to capture the reader's interest quickly and motivate them to take action.
    5. Each push notification should be equal or less than {push_length} characters.
    {"6. Please do not use emojis." if emoji == 'No' else "You can use emojis. But only one in the response."}
    7. Response in JSON format.

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

