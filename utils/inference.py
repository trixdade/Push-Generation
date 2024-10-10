import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

# Define the values for each column
geos = ['DE', 'NG', 'BD', 'BR', 'PL', 'GH', 'CA', 'HU']
sizes = ['360x240', '300x250', '300x100']
devices = ['mobile', 'desktop', 'tablet']
oses = ['android', 'ios', 'windows', 'mac_os']
os_versions = ['android 10', 'android 11', 'android 12', 'ios 16', 'windows 10']
browsers = ['chrome', 'samsung_internet', 'safari', 'safari_webview', 'chrome_webview']

# Generate random datetimes for 2024 with specific times of the day
def random_datetime_2024():
    # Random day of 2024
    random_day = random.randint(1, 180)  # first half of the year
    base_date = datetime(2024, 1, 1) + timedelta(days=random_day - 1)
    
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    return base_date + timedelta(hours=random_hour, minutes=random_minute, seconds=random_second)

# Adjusted OS version choices based on OS
os_versions_map = {
    'android': ['android 10', 'android 11', 'android 12'],
    'ios': ['ios 16'],
    'windows': ['windows 10'],
    'mac_os': ['mac_os catalina']
}

def generate_consistent_os_version(os):
    return random.choice(os_versions_map.get(os, [])) if os_versions_map.get(os) else None

def generate_random_dataframe(K):
    data = {
        'geo': [random.choice(geos) for _ in range(K)],
        'device': [random.choice(devices) for _ in range(K)],
        'os': [random.choice(oses) for _ in range(K)],
        'createdAt': [random_datetime_2024() for _ in range(K)]
    }

    # Ensure osVersion is consistent with os
    data['osVersion'] = [generate_consistent_os_version(os) for os in data['os']]
    data['browser'] = [random.choice(browsers) for _ in range(K)]

    df = pd.DataFrame(data)
    return df

def get_part_of_day(hour):
    if 4 <= hour < 8:
        return 'early_morning'
    elif 8 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 16:
        return 'afternoon'
    elif 16 <= hour < 20:
        return 'evening'
    elif 20 <= hour < 24:
        return 'late_evening'
    else:
        return 'night'

def preprocess_transactions(df):
    df['createdAt'] = pd.to_datetime(df['createdAt'], utc=True)
    df['createdAt'] = df['createdAt'].apply(lambda d: d.replace(tzinfo=None))
    
    # Day of the week
    df['day_of_week'] = df['createdAt'].dt.day_name()
    
    df['part_of_day'] = df['createdAt'].dt.hour.apply(get_part_of_day)
    
    # Business day
    df['is_business_day'] = df['createdAt'].dt.dayofweek < 5

    df.day_of_week = df.day_of_week.astype('category')
    df.part_of_day = df.part_of_day.astype('category')
    df = df.drop(columns=['createdAt'])

    return df
