import streamlit as st
import openai
import os
from openai import OpenAI
import pandas as pd
import json
import datetime

st.title("Casino & Betting Push Notification Generator")

# Input fields
geo = st.text_input("Geo (Geographic Location)", value='United Kingdom')
holiday_name = st.text_input("Holiday Name (if any)", value='World Cup')
offer = st.text_input("Offer (Value of Bonus Code or Discount)", value=20)
currency = st.text_input("Currency (if any)", value='%')
bonus_code = st.text_input("Bonus Code (if any)", value='CUP20')
language = st.text_input("Language", value='English')
title_len = st.text_input('Title length', value=30)
description_len = st.text_input('Description length', value=40)
push_num = st.text_input('Number of push notifications', value=5)
emoji = st.selectbox(
    'Do you need emojis in push?',
    ('Yes', 'No')
)
source = st.selectbox(
    'What source do you want to use?',
    ('20bet', '22bet', 'Bizzo Casino', 'National Casino')
)

if source in ['20bet', '22bet']:
    source_text = f'Betting named {source}'
elif source in ['Bizzo Casino', 'National Casino']:
    source_text = f'Casino named {source}'

user_reg = st.checkbox('User registered?')

client = OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

examples_for_prompt = """
        {{
            "title": "🎰Add 50FS to your WelcomePack"
            "desctiption": "Enter code 'THRILL'! Offer ends soon!💰"
        }},
        {{
            "title": "Welcome Pack Boost|+50FS more",
            "description": "Use code FROG|Slot of the Week Edition🐸"
        }},
        {{
            "title": "🎰National Casino Fest|Add 50FS",
            "description": "Type FEST for boost! Deal expires SOON💰"
        }}
""" if not user_reg else """
        {{
            "title": "🎰Summer Fest + 50% up to 100€"
            "desctiption": "Type FEST & join the fun! Limited time⏱️"
        }},
        {{
            "title": "🎰Vegas Weekend| Add Xtra 50FS",
            "description": "Type VEGAS for boosted deal! Ends SOON💰"
        }},
        {{
            "title": "🦸Bizzo | Use HERO for rewards",
            "description": "Superheroes Day w/ Super Prizes at Bizzo"
        }}
"""

emoji_examples_casino = "🎰 for title and 💰🤑⏱️ for the description"
emoji_examples_betting = "They could be based on input parameters."

emoji_examples = emoji_examples_casino 
if source in ['20bet', '22bet']:
    emoji_examples = emoji_examples_betting
else:
    emoji_examples = emoji_examples_casino

if emoji == 'No':
    emoji_text = "Please do not use emojis."
else:
    emoji_text = "You should use emojis. Each push should have one." + emoji_examples


# Function to generate push notifications
def generate_push_notifications(geo, holiday_name, offer, currency, 
                                bonus_code, language, title_len, description_len, push_num, emoji, user_reg):
    
    character_padding = 3

    title_len = int(title_len) - character_padding
    description_len = int(description_len) - character_padding
    
    prompt = f"""
    Task: Write short, creative push notifications for a {source_text}. Notifications should be engaging and highlighting that the offer is time-limited.
    Include a strong call to action (Get/Claim/Join/Enter code/Type/Use etc.), use wordplay, and incorporate humor to capture attention. 
    It is important to let the user know, that the offer is from {source_text}. It could be shown in text or emoji. In betting it could be done, by using the words "bet" or "odds". In casino it could be done, by using the words "casino", "slot", "free spins", "FS".
    Each notification must be based on the following parameters provided:

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
    {examples_for_prompt}

    Guidelines:
    1. Notifications should be concise and compelling.
    2. Incorporate playful language and humor where appropriate.
    3. Ensure the message aligns with the parameters given for each notification.
    4. Aim to capture the reader's interest quickly and motivate them to take action.
    5. Each push notification title should be equal or less than {title_len} characters.
    6. Each push notification description should be less than {description_len} characters
    7. You can write value of the bonus in the title if it is impressive.
    8. Write that offer is limited if applicable. For example, Offer ends soon/Time is limited/Now/Deal expires SOON/Deal Expire Tomorrow/ONLY TODAY/Code is only valid TODAY and etc.)
    9. {emoji_text}
    10. Response in JSON format.

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
            {"role": "system", "content": "You are a creative copywriter specializing in generating engaging push notifications."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        max_tokens=int(push_num) * (int(title_len) + int(description_len))
    )
    notifications = chat_completion.choices[0].message.content
    return notifications

# Button to generate notifications
if st.button("Generate Push Notifications"):
    if geo and holiday_name and offer and bonus_code and language and currency:
        notifications = generate_push_notifications(geo, holiday_name, offer, currency, 
                                bonus_code, language, title_len, description_len, push_num, emoji, user_reg)

        try:
            l = notifications.find('```json') + len('```json') if notifications.find('```json') != -1 else 0
            r = notifications.rfind('```') if notifications.find('```') != -1 else len(notifications)
            notifications_clean = notifications[l:r]
            notifications_json = json.loads(notifications_clean)

            df = pd.DataFrame(notifications_json)
            df['title_len'] = df.title.apply(len)
            df['description_len'] = df.description.apply(len)

            #st.text_area("Generated Push Notifications", notifications, height=300)
            st.dataframe(df)
        except:
            # save to file with datetime
            now = datetime.datetime.now()
            dt_string = now.strftime("%Y%m%d-%H%M%S")
            filename = f'notifications_{dt_string}.txt'
            with open(filename, 'w') as f:
                f.write(notifications)

    else:
        st.warning("Please fill in all input fields to generate push notifications.")

