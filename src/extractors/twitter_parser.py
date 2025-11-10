import requests
from typing import Dict

def parse_twitter_profile(username: str) -> Dict:
    """
    Extracts profile data from a given Twitter username.
    Replace with real scraping logic.
    """
    # In a real-world case, we would scrape data using Twitter's API or a web scraping tool.
    # Here we simulate the response.
    response = {
        "userId": "1845816542375682049",
        "isBlueVerified": True,
        "createdAt": "Mon Oct 14 13:19:17 +0000 2024",
        "followersCount": 46175,
        "favouritesCount": 22,
        "mediaCount": 81,
        "name": "Wall Street Pepe",
        "username": "WEPEToken",
        "statusesCount": 97,
        "profileImageUrlHttps": "https://pbs.twimg.com/profile_images/1846207382621188096/6Dqhjd7v_normal.png",
        "url": "https://t.co/4mmIhUXOeF",
        "pinnedTweetIds": ["1863905080426058015"]
    }
    return response