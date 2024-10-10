import streamlit as st
import openai
import pickle
import pandas as pd
import json
import datetime
import re
from utils.emoji import remove_unnecessary_emojis, replace_or_add_emoji
from utils.inference import generate_random_dataframe, preprocess_transactions
from utils.prompts import get_examples, get_emoji_text, get_reg_text, get_bonus_code_text, get_guidelines, generate_system_prompt
from utils.postprocessing import replace_abbr, filter_dataframe_by_offer, filter_dataframe_by_length

import numpy as np
from sentence_transformers import SentenceTransformer

from catboost import CatBoostClassifier


st.title("Casino & Betting Push Notification Generator")

language = 'English'
title_len = 30
description_len = 40
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
description_len = int(st.text_input('Description length', value=40))
push_num = int(st.text_input('Number of push notifications', value=5))
emoji = st.selectbox(
    'Do you need emojis in push?',
    ('Yes', 'No')
)
source = st.selectbox('What source do you want to use?',
    ('20bet', '22bet', 'Bizzo Casino', 'National Casino', 'Woo Casino', 
     'HellSpin', 'PlayAmo', 'TonyBet', 'Ivibet', 'Bob Casino', 'Vave', 
     'Avalon78', 'Betamo', 'Cookie Casino', 'Spinia', 'Mason Slots', 
     'CasinoChan', 'Bilucky', 'SupraPlay')
)

user_reg = st.checkbox('User registered?')

client = openai.OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

examples_for_prompt = get_examples(user_reg)
emoji_text = get_emoji_text(emoji)
reg_text = get_reg_text(user_reg, source, bonus_check, bonus_code)
bonus_code_text = get_bonus_code_text(bonus_check, bonus_code)
guidelines_default = get_guidelines(title_len, description_len, emoji_text, bonus_code_text, reg_text, creative=False)
guidelines_creative = get_guidelines(title_len, description_len, emoji_text, bonus_code_text, reg_text, creative=True)


# Function to generate push notifications
def generate_push_notifications(geo, holiday_name, offer, currency, 
                                bonus_code, language, title_len, description_len, push_num, creative=False):
    
    temperature = 0.8 if creative else 0.3
    
    character_padding = 2
    title_len = int(title_len) - character_padding
    description_len = int(description_len) - character_padding
    
    guidelines = guidelines_creative if creative else guidelines_default
    
    system_prompt = generate_system_prompt(source, examples_for_prompt, guidelines)
    
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
    3. Add name of the source
    4. Point out that offer is time limited
    5. Other rules
    """

    notifications = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="gpt-4o",
        max_tokens=int(push_num) * (int(title_len) + int(description_len)),
        response_format={"type": "text"},
        temperature=temperature
    )
    return notifications
    

# Button to generate notifications
if st.button("Generate Push Notifications"): 
    batch_size = 15
    whole_df = pd.DataFrame([])
    total_push_num = push_num
    generated_count = 0
    message = st.empty()
    generation_count_text = st.empty()
    generation_count = 0
    empty_generation = 0
    while generated_count < total_push_num:
        
        # если больше 7 эпох не можем сгенерировать пуши, то прекращаем их генерировать
        if empty_generation > 7:
            break
        
        current_push_num = min(batch_size, total_push_num - generated_count)
        message.write(f"Generating notifications {generated_count + 1} to {generated_count + current_push_num}")
        generation_count_text.write(f'Number of generations: {generation_count + 1}')
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
        generation_count += 1
        
        if generation_count > total_push_num + 5:
            st.write('Too much generations. Please reload the script or change the input parameters')
            break
        
        notifications_content = notifications.choices[0].message.content
        notifications_clear = notifications_content.replace('```json\n', '').replace('```', '')
        notifications_json = json.loads(notifications_clear)
        df = pd.DataFrame(notifications_json)
        
        # Удаление лишних эмодзи из заголовка
        df.title = df.title.apply(remove_unnecessary_emojis)
        
        # Если юзер не зареган, то добавляем эмодзи слот-машины
        if not user_reg:
            df.title = df.title.apply(replace_or_add_emoji)
        
        # Фильтрация строк без оффера
        df_offer = filter_dataframe_by_offer(df, ['title', 'description'], offer)
        # Фильтрация строк по длине title и description
        df_valid_length = filter_dataframe_by_length(df_offer, title_len, description_len)
        
        # Обновляем количество сгенерированных уведомлений
        generated_count += df_valid_length.shape[0]
        
        # убираем сокращения там, где это возможно
        if df_valid_length.shape[0] > 0:
            df_valid_length = replace_abbr(df_valid_length, title_len, description_len, bonus_check, bonus_code)
        else:
            empty_generation += 1
             
        whole_df = pd.concat([whole_df, df_valid_length])

    whole_df = whole_df.reset_index(drop=True)

    # SCORING PART
    st.write('Start scoring')
    
    titles = whole_df['title'].values
    descriptions = whole_df['description'].values
    
    # init model
    @st.cache_resource
    def load_labse_model():
        return SentenceTransformer('sentence-transformers/LaBSE')
    
    labse_model = load_labse_model()
    
    title_embeddings = labse_model.encode(titles)
    description_embeddings = labse_model.encode(descriptions)
    
    n_comp = 300
    with open('models/title_svd.pkl', 'rb') as file:
        title_svd = pickle.load(file)

    with open('models/desc_svd.pkl', 'rb') as file:
        desc_svd = pickle.load(file)

    title_embeddings_svd = title_svd.transform(title_embeddings)
    title_embeddings_svd_df = pd.DataFrame(data=title_embeddings_svd, columns=[f'PC_0_{i+1}' for i in range(n_comp)])

    description_embeddings_svd = desc_svd.transform(description_embeddings)
    description_embeddings_svd_df = pd.DataFrame(data=description_embeddings_svd, columns=[f'PC_1_{i+1}' for i in range(n_comp)])

    embs_df = pd.concat([title_embeddings_svd_df, description_embeddings_svd_df], axis=1)

    embs_df['title_embs'] = list(title_embeddings_svd)
    embs_df['desc_embs'] = list(description_embeddings_svd)

    
    # generate df of random users
    k = 300
    user_df = generate_random_dataframe(K=k)
    user_df = preprocess_transactions(user_df)
    user_df = user_df.drop_duplicates().reset_index(drop=True)
    
    catboost_model = CatBoostClassifier()
    catboost_model.load_model("models/catboost_10_10_v2.cbm")
    
    scores = []
    # concat user features with embeddings
    for _, emb_row in embs_df.iterrows():
        df_repeated = pd.concat([emb_row] * user_df.shape[0], ignore_index=True, axis=1).T
        inference_df = pd.concat([user_df, df_repeated], axis=1)
        
        predictions = catboost_model.predict_proba(inference_df)
        scores.append(np.mean(predictions[:,1]))
    
    whole_df['score'] = scores
    
    # sort df by score
    whole_df = whole_df.sort_values(by='score', ascending=False)
    
    message.empty()
    st.dataframe(whole_df)
    st.write(f'-------------------------------------------------------------')
    
    message_creative = st.empty()