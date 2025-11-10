import json
from extractors.twitter_parser import parse_twitter_profile
from outputs.exporters import export_to_json

def run_scraper(username):
    """
    Main function to initiate the scraping process for the given Twitter username.
    """
    profile_data = parse_twitter_profile(username)
    export_to_json(profile_data)

if __name__ == "__main__":
    username = input("Enter Twitter username to scrape: ")
    run_scraper(username)