import streamlit as st
import openai
import pandas as pd
import json
import datetime

st.title("Casino & Betting Push Notification Generator")


language = 'English'
title_len = 30
description_len = 50
push_num = 5
geo, holiday_name, offer, currency = None, None, None, None

# Input fields
geo = st.text_input("Geo (Geographic Location)", value='United Kingdom')
holiday_name = st.text_input("Holiday Name (if any)", value='World Cup')
offer = st.text_input("Offer (Value of Bonus Code or Discount)", value='20')
currency = st.text_input("Currency (if any)", value='%')
bonus_check = st.checkbox("Bonus Code")
bonus_code = st.text_input("Enter bonus code", value='CUP20') if bonus_check else None
language = st.text_input("Language", value='English')
title_len = st.text_input('Title length', value=30)
description_len = st.text_input('Description length', value=50)
push_num = int(st.text_input('Number of push notifications', value=5))
emoji = st.selectbox(
    'Do you need emojis in push?',
    ('Yes', 'No')
)
source = st.selectbox(
    'What source do you want to use?',
    ('20bet', '22bet', 'Bizzo Casino', 'National Casino')
)
user_reg = st.checkbox('User registered?')


client = openai.OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

def get_examples(user_reg):
    if not user_reg:
        return """
        {
            "title": "🎰Add 50FS to your Welcome Pack",
            "description": "THRILL! Register and enter code. Offer ends soon!💰"
        },
        {
            "title": "🎲Welcome Pack Boost|+50FS more",
            "description": "Register and use code FROG|Slot of the Week Edition🐸"
        },
        {
            "title": "🎲National Casino Fest|Add 50FS",
            "description": "Type FEST for boost! Deal expires SOON💰"
        }
        """
    else:
        return """
        {
            "title": "🎰Summer Fest + 50% up to 100€",
            "description": "Type FEST & join the fun! Limited time⏱️"
        },
        {
            "title": "🎰Vegas Weekend| Add Xtra 50FS",
            "description": "Type VEGAS for boosted deal! Ends SOON💰"
        },
        {
            "title": "🦸Bizzo | Use HERO for rewards",
            "description": "Superheroes Day w/ Super Prizes at Bizzo"
        }
        """

examples_for_prompt = get_examples(user_reg)

def get_source_text(source):
    if source in ['20bet', '22bet']:
        return f'Betting named {source}'
    else:
        return f'Casino named {source}'

source_text = get_source_text(source)

emoji_rules = """
There are the rules of how to place emojis properly:
1. If push contains words "Promotion, Offer, Deal, Reward, Special, Regular" 
then use these emojis: 💡 ⚡ 💯 🫶 🙌 ✅ ✨ 🎇 💪 💖 🆕 🆓 💸 💵 📣 🔆 🔜 

2. If push contains words "Spins, Jackpot, Slots, Games, Bet, Place a bet" 
then use these emojis: 🎰 🎲  

3. If push contains words "Money, Cash, Prize, Payout, Reward"
then use these emojis: 💸 💵 💰 

4. If push contains words "Birthday, Anniversary, Celebration, Party, Festival, Fest, Holiday, Special Day" 
then use these emojis: 🎂 🥳 🎈 🎇 🎆 🪩 

5. If push contains words "VIP, Exclusive, High Roller, Elite, Premier, Luxury, Privilege" 
then use these emojis: 👑 💎 🎯 🏆 🎇

6. If push contains words "Match, Game, Tournament, Championship, League, Contest, Competition"
then use these emojis: ⚽ 🥇 🏆 💪 and countries flags

7. If push contains words "Time-Limited, Limited, Hurry, Ends Soon, Time is running out, Only TODAY, Today only, Now, Last Chance" 
then use these emojis: ⏳ ⏰ 🔔 ⌛ ⏱️ 🔜

8. If push contains words "Summer, Wildwest, Oktoberfest, Sweet, Seasonal, Holiday, Festival"
then use these emojis: 🤠 🏖️ 🍺 🍬 🍭 🌠 🎇 🎆 🪄  🪩 and countries flags (if it is local holiday)

9. If push contains words "Unique, Special, Exclusive, Grand, Huge" 
then use these emojis: 🧨 💣 💥 ⚡

10. If push contains words "New, Fresh, Special, Launch, Release, Introduce, Unveiling"
then use these emojis: 🆕 📣 💎💡 
"""

def get_emoji_text(emoji, source):
    emoji_examples_casino = "🎰 for title and 💰🤑⏱️ for the description"
    emoji_examples_betting = "They could be based on input parameters."

    emoji_examples = emoji_examples_casino if source not in ['20bet', '22bet'] else emoji_examples_betting

    if emoji == 'No':
        return "Make sure you do not use emojis."
    else:
        return "You must use emojis based on the generated text." + '\n' + emoji_rules

emoji_text = get_emoji_text(emoji, source)


# Function to generate push notifications
def generate_push_notifications(geo, holiday_name, offer, currency, 
                                bonus_code, language, title_len, description_len, push_num):
    
    character_padding = 3

    title_len = int(title_len) - character_padding
    description_len = int(description_len) - character_padding
    
    system_prompt = f"""You are a creative copywriter specializing in generating engaging push notifications.
    
    Task: Write short, creative push notifications for a {source_text}. Notifications should be engaging and highlighting that the offer is time-limited.
    Include a strong call to action (Get/Claim/Join/Enter code/Type/Use etc.), use wordplay, and incorporate humor to capture attention. 
    It is important to let the user know, that the offer is from {source_text}. It could be shown in text or emoji. 
    In betting it could be done, by using the words "bet" or "odds". In casino it could be done, by using the words "casino", "slot", "free spins", "FS".
    Each notification must be based on the following parameters provided:

    Geo: The geographic location of the target audience.
    Holiday Name: The name of a holiday if there is one, to make the message relevant to current events.
    Offer: The actual value of the bonus code or discount being offered. Could be in %, but limited in some currency.
    Bonus Code: A specific code to be used if there is one. Don't make up your own bonus code.
    Language: The language in which the notification should be written.
    Currency: The currency relevant to the offer, if applicable.

    Format the response as a JSON array with each notification having a "title" and "description".
    Format:
    [
        {{
            "title": "title_1"
            "description": "description_1"
        }}, 
        {{
            "title": "title_2"
            "description": "description_2"
        }}
    ]

    Example:
    {examples_for_prompt}

    Guidelines:
    1. Notifications should be concise and compelling.\n
    2. Incorporate playful language and humor where appropriate.\n
    3. Ensure the message aligns with the parameters given for each notification.\n
    4. Aim to capture the reader's interest quickly and motivate them to take action.\n
    5. Each push notification title should be equal or less than {title_len} characters.\n
    6. Each push notification description should be less than {description_len} characters\n
    7. You can write value of the bonus in the title if it is impressive.\n
    8. Write that offer is limited if applicable. For example, you can add phrases like Offer ends soon, 
    Time is limited, Now, Deal expires SOON, Deal Expire Tomorrow, ONLY TODAY, Code is only valid TODAY and etc.\n
    9. {emoji_text}\n
    10. {"There is no bonus code in this push notification. Please do not make up your own bonus codes." if not bonus_check else f"Add bonus code {bonus_code} somewhere in beginning of the description."}
    11. {"Skip." if user_reg else f"You have to let people know, that this is push from {source_text.lower()}. Also, you could add that user have to register to use promocode, if applicable."}\n
    12. Response in JSON list format.\n
    """
    
    user_prompt = f"""
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
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="gpt-4o",
        max_tokens=int(push_num) * (int(title_len) + int(description_len)),
        response_format={"type": "text"},
        temperature=0.4
    )
    notifications = chat_completion
    return notifications

# Button to generate notifications
if st.button("Generate Push Notifications"): 
    batch_size = 15
    whole_df = pd.DataFrame([])
    for i in range(0, push_num, batch_size):
        current_push_num = min(batch_size, push_num - i)
        st.write(f"Generating notifications {i + 1} to {i + current_push_num}")
        notifications = generate_push_notifications(
            geo, 
            holiday_name, 
            offer, 
            currency, 
            bonus_code, 
            language, 
            title_len, 
            description_len, 
            current_push_num
        )
        
        try:
            notifications_content = notifications.choices[0].message.content
            notifications_clear = notifications_content.replace('```json\n', '').replace('```', '')
            notifications_json = json.loads(notifications_clear)
            df = pd.DataFrame(notifications_json)
            whole_df = pd.concat([whole_df, df])

        except json.JSONDecodeError:
            # save to file with datetime
            now = datetime.datetime.now()
            dt_string = now.strftime("%Y%m%d-%H%M%S")
            filename = f'notifications_{dt_string}.txt'
            with open(filename, 'w') as f:
                f.write(notifications)
             
    whole_df = whole_df.reset_index(drop=True)
    st.dataframe(whole_df)
