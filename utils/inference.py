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
    
    # Choose random time of the day (morning: 6-12, night: 0-6, other: 12-24)
    time_of_day = random.choice([
        (6, 12),  # Morning
        (0, 6),   # Night
        (12, 24)  # Other
    ])
    random_time = random.randint(time_of_day[0], time_of_day[1] - 1)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    return base_date + timedelta(hours=random_time, minutes=random_minute, seconds=random_second)

# Updating the function to ensure that the 'os' and 'osVersion' are consistent

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
        #'size': [random.choice(sizes) for _ in range(K)],
        'device': [random.choice(devices) for _ in range(K)],
        'os': [random.choice(oses) for _ in range(K)],
        'createdAt': [random_datetime_2024() for _ in range(K)]
    }

    # Ensure osVersion is consistent with os
    data['osVersion'] = [generate_consistent_os_version(os) for os in data['os']]
    data['browser'] = [random.choice(browsers) for _ in range(K)]

    df = pd.DataFrame(data)
    return df


# Part of the day
def get_part_of_day(hour):
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'midday'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'
    
    # Season
def get_season(date):
    Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
    seasons = [
        (pd.Timestamp(Y, 1, 1), pd.Timestamp(Y, 3, 20), 'winter'),
        (pd.Timestamp(Y, 3, 21), pd.Timestamp(Y, 6, 20), 'spring'),
        (pd.Timestamp(Y, 6, 21), pd.Timestamp(Y, 9, 22), 'summer'),
        (pd.Timestamp(Y, 9, 23), pd.Timestamp(Y, 12, 20), 'fall'),
        (pd.Timestamp(Y, 12, 21), pd.Timestamp(Y, 12, 31), 'winter')
    ]
    date = date.replace(year=Y)
    return next(season for start, end, season in seasons if start <= date <= end)
        
def preprocess_transactions(transactions):
    # Convert to datetime and remove timezone information
    transactions['createdAt'] = pd.to_datetime(transactions['createdAt'], utc=True)
    transactions['createdAt'] = transactions['createdAt'].apply(lambda d: d.replace(tzinfo=None))
    
    # Day of the week
    transactions['day_of_week'] = transactions['createdAt'].dt.day_name()

    transactions['part_of_day'] = transactions['createdAt'].dt.hour.apply(get_part_of_day)

    # Month
    transactions['month'] = transactions['createdAt'].dt.month

    #transactions['season'] = transactions['createdAt'].apply(get_season)

    # Business day
    transactions['is_business_day'] = transactions['createdAt'].dt.dayofweek < 5

    # One-hot encoding for categorical columns
    # transactions = pd.get_dummies(transactions, columns=['device', 'osVersion', 'browser', 'day_of_week', 'part_of_day', 'geo'])
    
    # transactions = transactions.drop(columns=['city', 'os', 'createdAt', 'month'], errors='ignore')

    return transactions


def inference(df):
    catboost_model = CatBoostClassifier()
    catboost_model.load_model("catboost.cbm")
    
    

    predictions = catboost_model.predict_proba(df)
    return predictions