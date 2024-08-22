import streamlit as st
import openai
import pandas as pd
import json
import datetime
import re
from utils.emoji import remove_unnecessary_emojis

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
title_len = int(st.text_input('Title length', value=30))
description_len = int(st.text_input('Description length', value=50))
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
            "description": "THRILL! Register and enter code. Limited!💰"
        },
        {
            "title": "🎰Welcome Pack Boost|+50FS more",
            "description": "Register and use code FROG|Slot of the Week Edition🐸"
        },
        {
            "title": "🎲National Casino Fest|Add 50FS",
            "description": "Join and type FEST for boost! Hurry⏱️"
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

emoji_rules = """
There are the rules of how to place emojis properly:
1. If push contains words "Promotion, Offer, Deal, Reward, Special, Regular" 
then use these emojis: 💡 ⚡ 💯 🫶 🙌 ✅ ✨ 🎇 💪 💖 🆕 🆓 💸 💵 📣 🔆 🔜 

2. If push contains words "Casino, Spins, Jackpot, Slots, Games, Bet, Place a bet" 
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

def get_emoji_text(emoji):
    if emoji == 'No':
        return "Make sure you do not use emojis."
    else:
        return "You must use emojis based on the generated text. Please DO NOT use more than 1 emoji in title!" + '\n' + emoji_rules

emoji_text = get_emoji_text(emoji)

def get_reg_text(user_reg, source):
    reg_text = 'Be sure that you done all the guidelines.'
    if not user_reg:
        if source in ['20bet', '22bet']: 
            reg_text += f"""You must let user know, that this is notification from {source}. Add this name somewhere.
            Be sure that you do it."""
        else:
            reg_text += f"""You must let user know, that this is notification from casino.
            Do it by adding slot emoji (🎰) in the beginning or by using words 
            like casino, bet, odds, free spins or just add the name of casino: {source}. 
            Be sure that you do it."""
        
    if bonus_check:
        bonus_check_text = f"You could mention, that user should register to enter bonus code: {bonus_code}"
        reg_text += f'\n{bonus_check_text}' 
            
    return reg_text
    
reg_text = get_reg_text(user_reg=user_reg, source=source)


# POSTPROCESSING FUNCS
def filter_dataframe_by_offer(df, columns, offer):
    mask = df[columns].apply(lambda row: any(offer in str(row[col]) for col in columns), axis=1)
    
    # Фильтрация датафрейма по маске
    filtered_df = df[mask]
    return filtered_df

def len_with_emojis(text):
    """
    Подсчитывает длину строки, учитывая, что каждый эмодзи считается за 2 символа.
    
    :param text: Строка, длину которой нужно подсчитать.
    :return: Длина строки с учетом эмодзи.
    """
    # Регулярное выражение для поиска эмодзи
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # Эмодзи со смайликами
        "\U0001F300-\U0001F5FF"  # Символы и пиктограммы
        "\U0001F680-\U0001F6FF"  # Транспортные средства и символы
        "\U0001F1E0-\U0001F1FF"  # Флаги (с помощью пар региональных индикаторов)
        "\U00002702-\U000027B0"  # Разные символы и пиктограммы
        "\U000024C2-\U0001F251"  # Другие символы
        "]+", flags=re.UNICODE)

    # Находим все эмодзи в тексте
    emojis = emoji_pattern.findall(text)
    
    # Считаем длину строки
    total_length = len(text)
    
    # Корректируем длину, добавляя 1 за каждый эмодзи
    emoji_count = len(emojis)
    adjusted_length = total_length + emoji_count
    
    return adjusted_length

def filter_dataframe_by_length(df, title_len, description_len):
    mask = (df['title'].apply(len_with_emojis) <= title_len) & (df['description'].apply(len_with_emojis) <= description_len)
    filtered_df = df[mask]
    return filtered_df


def replace_abbr(df, title_len, description_len):
    df['title_len'] = df['title'].apply(len_with_emojis)
    df['description_len'] = df['description'].apply(len_with_emojis)
    
    # free spins addition
    fs_len = len(' Free Spins') - len('FS')
    code_len = len(' code')
    # add the word 'code' if applicable 
    if bonus_check:
        df.title = df.apply(lambda row: row.title.replace(bonus_code, bonus_code + ' code') 
                            if row.title_len + code_len < title_len else row.title, axis=1)
        
        df.description = df.apply(lambda row: row.description.replace(bonus_code, bonus_code + ' code') 
                                if row.description_len + code_len < description_len else row.description, axis=1)
    
    # refresh length
    df['title_len'] = df['title'].apply(len_with_emojis)
    df['description_len'] = df['description'].apply(len_with_emojis)
    
    # change FS 
    df.title = df.apply(lambda row: row.title.replace('FS', ' Free Spins') 
                        if row.title_len + fs_len < title_len else row.title, axis=1)
    
    df.description = df.apply(lambda row: row.description.replace('FS', ' Free Spins') 
                              if row.description_len + fs_len < description_len else row.description, axis=1)
    
    # remove whitespaces
    cols = ['title', 'description']
    df[cols] = df[cols].apply(lambda x: x.str.strip())
    
    # remove created cols
    df = df.drop(columns=['title_len', 'description_len'])

    return df


# Function to generate push notifications
def generate_push_notifications(geo, holiday_name, offer, currency, 
                                bonus_code, language, title_len, description_len, push_num):
    
    character_padding = 2

    title_len = int(title_len) - character_padding
    description_len = int(description_len) - character_padding
    
    system_prompt = f"""You are a creative copywriter specializing in generating engaging push notifications.
    
    Task: Write short, creative push notifications for a project name {source}. Notifications should be engaging and highlighting that the offer is time-limited.
    Include a strong call to action, e.g. get/claim/join/enter/type/use. Use wordplay and incorporate humor to capture attention. 
    Each notification must be based on the following parameters provided:

    Geo: The geographic location of the target audience.
    Holiday Name: The name of a holiday or some special day if there is one, to make the message relevant to current events. Could be sports events, classic holidays or just special days.
    Offer: The actual value of the bonus code or discount being offered. Could be in %, but limited in some currency.
    Currency: The currency relevant to the offer, if applicable.
    Bonus Code: A specific code to be used if there is one. Don't make up your own bonus code.
    Language: The language in which the notifications should be written.

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
    7. Each emoji is 2 characters, so be aware of it.
    8. You can write value of the bonus in the title if it is impressive.\n
    9. Properly write offer, word by word. Don't split the words within.
    10. Write that offer is limited if applicable. Add phrases like offer ends soon, 
    time is limited, now, deal expires soon, only today and etc. Try to make this time-related text short.\n
    11. {emoji_text}\n
    12. {"There is no bonus code in this push notification. Please do not make up your own bonus codes." if not bonus_check else f"Be sure, that you add bonus code '{bonus_code}' somewhere in the beginning of the description."}
    13. {reg_text}
    14. Please make sure that you wrote Offer fully word by word. Do not split it, just paste it somewhere.
    15. Put bonus code in the beggining of title or description, do not put it at the end.
    16. Response in JSON list format.\n
    """
    
    user_prompt = f"""
    Generate {push_num} push notifications in {language} language, using these placeholders:
    1. Geo: {geo}
    2. Holiday Name: {holiday_name}
    3. Offer: {offer}
    4. Bonus Code: {bonus_code}
    5. Language: {language}
    6. Currency: {currency}
    
    Make sure, that you fully add {offer} into every description or title.
    
    Prority in push:
    1. Add call to action
    2. Try to incorporate Holiday Name creatively when generating the text
    3. Point out that offer is time limited
    4. Other rules
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="gpt-4o",
        max_tokens=int(push_num) * (int(title_len) + int(description_len)),
        response_format={"type": "text"},
        temperature=0.1
    )
    notifications = chat_completion
    return notifications

# Button to generate notifications
if st.button("Generate Push Notifications"): 
    batch_size = 15
    whole_df = pd.DataFrame([])
    total_push_num = push_num
    generated_count = 0
    while generated_count < total_push_num:
        current_push_num = min(batch_size, total_push_num - generated_count)
        st.write(f"Generating notifications {generated_count + 1} to {generated_count + current_push_num}")
        
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
        
        notifications_content = notifications.choices[0].message.content
        notifications_clear = notifications_content.replace('```json\n', '').replace('```', '')
        notifications_json = json.loads(notifications_clear)
        df = pd.DataFrame(notifications_json)
        
        # Удаление лишних эмодзи из заголовка
        print('удаляем эмодзи')
        df.title = df.title.apply(remove_unnecessary_emojis)
        
        # Фильтрация строк без оффера
        print('фильтруем без оффера')
        df_offer = filter_dataframe_by_offer(df, 
                                             columns=['title', 'description'], 
                                             offer=offer)
        
        removed_offer_count = df.shape[0] - df_offer.shape[0]
        st.write(f'Removed {removed_offer_count} without offer')
        
        # Фильтрация строк по длине title и description
        df_valid_length = filter_dataframe_by_length(df_offer, title_len=title_len, description_len=description_len)
        removed_length_count = df_offer.shape[0] - df_valid_length.shape[0]
        st.write(f'Removed {removed_length_count} due to length constraints')
        
        st.write(f'-------------------------------------------------------------')
        # Обновляем количество сгенерированных уведомлений
        generated_count += df_valid_length.shape[0]
        
        
        # убираем сокращения там, где это возможно
        print('убираем сокращения')
        df_valid_length = replace_abbr(df_valid_length, title_len=title_len, description_len=description_len)
        
        whole_df = pd.concat([whole_df, df_valid_length])
        
        removed_total = removed_offer_count + removed_length_count
        # Если были удаленные строки, пересчитываем их для генерации
        if removed_total > 0:
            st.write(f"Regenerating {removed_total} notifications...")
             
    whole_df = whole_df.reset_index(drop=True)
    
    whole_df['title_len'] = whole_df['title'].apply(len_with_emojis)
    whole_df['description_len'] = whole_df['description'].apply(len_with_emojis)
    st.dataframe(whole_df)
