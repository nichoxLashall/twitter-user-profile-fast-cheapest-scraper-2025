import json
import logging
from src.extractors.twitter_parser import TwitterParser
from src.outputs.exporters import Exporter
from src.config import settings
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_input_usernames(input_file: str) -> list[str]:
    """Load usernames from a text file."""
    if not Path(input_file).exists():
        logging.error(f"Input file '{input_file}' not found.")
        return []
    with open(input_file, "r", encoding="utf-8") as f:
        return [line.strip().lstrip("@") for line in f if line.strip()]

def main():
    input_path = "data/inputs.sample.txt"
    output_path = "data/sample.json"

    usernames = load_input_usernames(input_path)
    if not usernames:
        logging.warning("No usernames found in input file.")
        return

    parser = TwitterParser(settings.API_ENDPOINT, settings.TIMEOUT)
    exporter = Exporter(output_path)

    results = []
    for username in usernames:
        try:
            logging.info(f"Scraping user: {username}")
            profile = parser.fetch_user_profile(username)
            results.append(profile)
        except Exception as e:
            logging.error(f"Error scraping {username}: {e}")

    exporter.export(results)
    logging.info(f"Scraping complete. Exported {len(results)} profiles to {output_path}")

if __name__ == "__main__":
    main()