import json
from src.extractors.twitter_parser import TwitterParser
from src.outputs.exporters import Exporter
from src.config import settings

def test_twitter_parser_output_format(tmp_path):
    parser = TwitterParser(settings.API_ENDPOINT, settings.TIMEOUT)
    result = parser.fetch_user_profile("testuser")
    assert "userId" in result
    assert "username" in result
    assert result["username"] == "testuser"

    output_file = tmp_path / "out.json"
    exporter = Exporter(str(output_file))
    exporter.export([result])
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["username"] == "testuser"