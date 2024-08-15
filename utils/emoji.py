import re

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