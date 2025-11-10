import json

def export_to_json(data: dict, filename: str = "output.json"):
    """
    Exports the scraped Twitter profile data to a JSON file.
    """
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    print(f"Data successfully exported to {filename}")