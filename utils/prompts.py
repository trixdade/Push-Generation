def get_examples(user_reg):
    if not user_reg:
        return """
        {
            "title": "🎰Add 50FS to your Welcome Pack",
            "description": "THRILL! Enter code at Bizzo Casino|Limited!💰"
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
        
def get_emoji_text(emoji):
    if emoji == 'No':
        return "Make sure you do not use emojis."
    else:
        return """You must use emojis based on the generated text. Add insteresting emojis to the description, that fits the text.
                    It can be flags, time-related emojis, crowns, diamonds etc.
                    Please DO NOT use more than 1 emoji in title!"""
                    
def get_reg_text(user_reg, source, bonus_check, bonus_code):
    reg_text = f'Be sure that you done all the guidelines. Let user know, that this is notification from {source}'
    if not user_reg:
        reg_text += f"""You must let user know, that this is notification from {source}.
        Do it by using words like casino, bet, odds, free spins or just add the name of casino: {source}. 
        Be sure that you do it."""
        
    if bonus_check:
        bonus_check_text = f"You could mention, that user should register to enter bonus code: {bonus_code}"
        reg_text += f'\n{bonus_check_text}' 
            
    return reg_text

def get_bonus_code_text(bonus_check, bonus_code):
    if not bonus_check:
        text = "There is no bonus code in this push notification. Please do not make up your own bonus codes." 
    else:
        text = f"""Be sure, that you add bonus code '{bonus_code}' in the beginning of the description. Do not put the code at the end.
             You could add get/claim/join/enter/type/use before code."""
             
             
def get_guidelines(title_len, description_len, emoji_text, bonus_code_text, reg_text, creative):
    guidelines = f"""
        Guidelines:
        1. Notifications should be concise and compelling.\n
        2. Incorporate playful language and humor where appropriate.\n
        3. Ensure the message aligns with the parameters given for each notification.\n
        5. Each push notification title should be equal or less than {title_len} characters.\n
        6. Each push notification description should be equal or less than {description_len} characters\n  
        7. {emoji_text}
        8. {bonus_code_text}
        9. {reg_text}
    """
    
    if not creative:
        guidelines += f"""
            10. Properly write Offer, word by word. Don't split it, just paste it somewhere.
            11. Write that offer is limited if applicable. Add phrases like offer ends soon, 
            time is limited, now, deal expires soon, only today and etc. Try to make this time-related text short.\n
        """
    return guidelines


def generate_system_prompt(source, examples_for_prompt, guidelines):
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

    {guidelines}
    
    Response in JSON list format!
    """
    
    return system_prompt