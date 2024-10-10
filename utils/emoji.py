import re


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

def replace_or_add_emoji(text):
    # Регулярное выражение для поиска эмодзи в начале строки
    emoji_pattern = r'^[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251\U0001F004\U0001F0CF\U0001F170-\U0001F171\U0001F17E-\U0001F17F\U0001F18E\U0001F191-\U0001F19A\U0001F1E6-\U0001F1FF\U0001F201-\U0001F202\U0001F21A\U0001F22F\U0001F232-\U0001F23A\U0001F250-\U0001F251\U0001F004\U0001F0CF\U0001F3E0-\U0001F3FF\U0001F004]+'

    # Эмодзи слот-машины 🎰
    slot_machine_emoji = "🎰"

    # Проверка наличия эмодзи в начале текста
    if re.match(emoji_pattern, text):
        # Удаляем эмодзи и добавляем слот-машину
        return re.sub(emoji_pattern, slot_machine_emoji, text, count=1)
    else:
        # Добавляем слот-машину в начало текста
        return slot_machine_emoji + text

def remove_unnecessary_emojis(text):
    # Регулярное выражение для поиска эмодзи
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # Эмодзи со смайликами
        "\U0001F300-\U0001F5FF"  # Символы и пиктограммы
        "\U0001F680-\U0001F6FF"  # Транспортные средства и символы
        "\U0001F1E0-\U0001F1FF"  # Флаги (с помощью пар региональных индикаторов)
        "\U00002702-\U000027B0"  # Разные символы и пиктограммы
        "\U000024C2-\U0001F251"  # Другие символы
        "]+", flags=re.UNICODE)
    
    # Найти первое эмодзи
    first_match = emoji_pattern.search(text)
    
    if not first_match:
        return text  # Возвращаем исходный текст, если эмодзи не найдено

    # Индекс первого эмодзи
    first_emoji = first_match.group(0)
    
    # Создаем новую строку, в которой все эмодзи после первого удалены
    result_text = text[:first_match.start()] + first_emoji + emoji_pattern.sub("", text[first_match.end():])
    
    return result_text

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