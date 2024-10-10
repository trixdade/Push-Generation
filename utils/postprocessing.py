import re
from utils.emoji import len_with_emojis


def filter_dataframe_by_length(df, title_len, description_len):
    mask = (df['title'].apply(len_with_emojis) <= title_len) & (df['description'].apply(len_with_emojis) <= description_len)
    filtered_df = df[mask]
    return filtered_df

def filter_dataframe_by_offer(df, columns, offer):
    mask = df[columns].apply(lambda row: any(offer in str(row[col]) for col in columns), axis=1)
    
    # Фильтрация датафрейма по маске
    filtered_df = df[mask]
    return filtered_df

def capitalize_sentences(text):
    def capitalize_first_letter(sentence):
        # Найдем первую букву в предложении и сделаем её заглавной
        for i, char in enumerate(sentence):
            if char.isalpha():  # Проверяем, является ли символ буквой
                return sentence[:i] + char.upper() + sentence[i+1:]
        return sentence  # Если буквы не найдены, возвращаем предложение как есть

    # Разбиваем текст на предложения, используя регулярное выражение
    sentences = re.split('(?<=[.!?]) +', text)
    
    # Применяем функцию к каждому предложению
    capitalized_sentences = [capitalize_first_letter(sentence) for sentence in sentences]
    
    # Собираем предложения обратно в текст
    capitalized_text = ' '.join(capitalized_sentences)
    
    return capitalized_text

def replace_abbr(df, title_len, description_len, bonus_check, bonus_code):
    df['title_len'] = df['title'].apply(len_with_emojis)
    df['description_len'] = df['description'].apply(len_with_emojis)
    
    # free spins addition
    fs_len = len(' Free Spins') - len('FS')
    code_len = len(' code')
    # add the word 'code' if applicable 
    if bonus_check:
        df.title = df.apply(lambda row: row.title.replace(bonus_code, 'code ' + bonus_code) 
                            if row.title_len + code_len < title_len else row.title, axis=1)
        df.title = df.apply(lambda row: row.title.replace('code code', 'code'), axis=1)
        df.title = df.title.apply(capitalize_sentences)
        
        df.description = df.apply(lambda row: row.description.replace(bonus_code, 'code ' + bonus_code)
                                if row.description_len + code_len < description_len else row.description, axis=1)
        df.description = df.apply(lambda row: row.description.replace('code code', 'code'), axis=1)
        df.description = df.description.apply(capitalize_sentences)
    
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
